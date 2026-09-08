<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:16:10Z UTC
     agent id aec1e3f28a738e5e6 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aec1e3f28a738e5e6.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

## Worker

**W21c** — corpus-differential lane, third pass, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable observed names a served model; the coordinator must extract the actual per-child runtime model from the transcript. Do not treat this line as observed fact.

`date -u` at **start**: `Tue Sep  8 03:04:06 UTC 2026`
`date -u` at **end**: `Tue Sep  8 03:07:50 UTC 2026` (report drafting continued past this stamp; no further tool call touched the repository)

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (verbatim; the same command at end returned the same set, unchanged):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
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
GLOBAL_AGENT_NO_PROXY=<same no_proxy list>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=<proxy/truststore flags>
NO_PROXY=<same no_proxy list>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<same no_proxy list>
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**Actual HEAD read — it moved twice under me.**

| Point | HEAD |
|---|---|
| `git rev-parse HEAD` at my **start** (my audit set is pinned here) | `a87275c14897230041fde97c9965c9646474df7a` |
| `git rev-parse HEAD` at my **end** | `98a0833f1ede2cf9cef13790388260567a32e868` (`Campaign: W25 candidate-merit check — novelty fails, statistics hold`) |
| `COMMON-BRIEF.md`'s declared freeze | `92abbcb905cacf07f14b238db50d1b98f6590374` — not HEAD at any point I observed |
| W21b's HEAD | `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d` |
| Corpus snapshot base | `93b75888e31976195145e2404373b2d7a512f6d1` — not tested locally this run |

`git status --porcelain | wc -l` → **0 at start and 0 at end.** I wrote nothing into `/home/user/Rare-cancers`. All scratch under `/tmp/claude-0/w21c/`. No git write operation, no network, no paid API, no GPU, no MCP call, no `preflight.sh`.

---

## Question

**Do the campaign reports collected since W21b ran carry any novelty or absence claim that the frozen corpus or the live tree contradicts?**

Open because W21 audited the 48 present at `47aac85f…` and W21b the 36 new at `3f5fc95d…`; the collected set had grown to 107 at my dispatch and 108 by my first listing, and none of the additions had been tested against either source.

---

## Prior-work check

```
$ git ls-tree --name-only 47aac85f… .../reports/ | wc -l        → 48    (W21's set)
$ git ls-tree --name-only 3f5fc95d… .../reports/ | wc -l        → 85    (set at W21b)
$ ls .../reports | sort | wc -l                                  → 108   (at my start)
$ comm -13 at-w21b-85.txt now-108.txt | wc -l                    → 23
```

**Set 1 — W21's 48 (not re-audited; W21's verdicts stand):** `W01`, `W01b`, `W01c`, `W01d`, `W02`, `W02b`, `W02c`, `W03`, `W03b`, `W04`, `W04b`, `W04c`, `W05`, `W05b`, `W05c`, `W06`, `W06b`, `W06c`, `W07`, `W07b`, `W08`, `W08b`, `W08c`, `W09`, `W09b`, `W10`, `W10b`, `W10c`, `W11`, `W11b`, `W12`, `W13`, `W13b`, `W14`, `W15`, `W15b`, `W15c`, `W16`, `W16b`, `W17`, `W17b`, `W17c`, `W19`, `W19b`, `W19c`, `W20`, `W20b`, `W20c`.

**Set 2 — W21b's 36 (not re-audited; W21b's verdicts stand):** `W01e`, `W02d`, `W03c`, `W03d`, `W05d`, `W06d`, `W07c`, `W07d`, `W08d`, `W08e`, `W09c`, `W09d`, `W10d`, `W10e`, `W11c`, `W11d`, `W12b`, `W12c`, `W13c`, `W13d`, `W13e`, `W14b`, `W14c`, `W15d`, `W15e`, `W16c`, `W17d`, `W17e`, `W17f`, `W17g`, `W18`, `W19d`, `W20d`, `W20e`, `W22`, `W23` (+ `W21` itself, excluded by W21b as the prior work it extended).

**Set 3 — new since W21b, 23 files; I audited 22**, excluding `W21b-corpus-differential-second-pass.md` itself as the prior work I am extending, not an object of audit:
`W01f-obtainable-band-stability.md`, `W02e-endothelial-variance-decomposition.md`, `W04d-duration-set-stability.md`, `W05e-immunosarc-pair-adjudication.md`, `W05f-window-arithmetic-audit.md`, `W06e-margin-to-reversal-ranking.md`, `W07e-denominator-claim-second-axis.md`, `W08f-full-adjudication-envelope.md`, `W08g-borderline-pmid-recovery.md`, `W08h-remaining-missing-value-calls.md`, `W09e-views-blast-radius.md`, `W10f-reachability-disagreement-reconciliation.md`, `W12d-stdout-defect-fix-shape.md`, `W13f-cross-file-gate-coverage.md`, `W14d-fourth-cohort-guard-repair.md`, `W15f-radiotherapy-denominator-scope.md`, `W16d-unpinned-pooled-figures.md`, `W17h-welch-coverage-census.md`, `W19e-dbd-family-prespecified-test.md`, `W19f-cross-5prime-falsification.md`, `W19g-leave-one-peakset-out.md`, `W20f-probe-intersection-filter.md`.

**Three further reports landed during my run and are OUT of my audited set, untested by anyone:** `W22b-final-provenance-ledger.md`, `W24-repair-routing-index.md`, `W25-gse243553-candidate-merit.md` (the reports directory went 107 → 108 → 111 while I worked). `W24` is known to contain at least one EGAS accession string; it is unaudited.

**I re-audited none of W21's 48 and none of W21b's 36.** `CLOSED-WORK.md` read in full. Not replayed, re-reviewed or relabelled: the blocked NR4A Perspective refusal (not approached under any label or framing); the user-rejected registry ICD-O paper; Davis / Hofvander / promoter-transfer / inverse-bounds closures; every unrecovered source (I fetched nothing and used no network); the lane-11 source-index bundle (absence claims tested only, no change proposed). `PRJNA692081` / `SRP301712` are **ALREADY RECOVERED → DUPLICATE, never novelty**; I report no accession-derived finding and draw no cohort, independence or patient conclusion. The junction-source directory's own README records that its access-and-identity gate was **not passed**; I treat its presence in the corpus as a provenance fact only.

---

## Method / inputs

- **Live checkout** `/home/user/Rare-cancers`, read-only (`git ls-files`, `git ls-tree`, `git log`, `grep`, `sed`, `python3` for slicing two JSON files). Pinned at `a87275c1…`.
- **Frozen corpus** `/tmp/claude-0/frozen-corpus/extracted/corpus/` — read **in place**, not copied, not overlaid. Repository-relative root as given in my dispatch; `metadata/tracked-file-map.txt` also read.
- **Scratch** `/tmp/claude-0/w21c/` — `corpus-files.txt` (5,996), `live-files.txt` (7,717), `corpus-only.txt` (2,201), the three report sets, `claims.txt` (39).
- **Claim pool:** one regex sweep over the 22 new reports → **39 candidate lines in 17 files**; 5 reports produced no matching line (`W02e`, `W06e`, `W15f`, `W17h`, `W19f`).
- No network, no retrieval, no external source, no repository gate run.

---

## Result

### R1 — Verdict table, 22 new reports (`PRIMARY` unless marked)

| # | Report `file:line` | Claim (quoted, abridged) | Verdict / falsifying source |
|---|---|---|---|
| M1 | `W01f-obtainable-band-stability.md:132` | *"row 8's entire class (the supporting directory is **absent here and from the frozen corpus**)"* | **CONTRADICTED — by the CORPUS.** The directory is present as 13 corpus-only files, `retrieval.json` among them (R2) |
| M2 | `W01f:128` | *"W01e D4 found no committed anchor (**the tree's only EGA accession is Haller's**, not EMC)"* | **CONTRADICTED — by the LIVE TREE.** Five distinct EGAS accessions are committed outside the campaign reports (R3). This is W21b's N2 defect propagated into a second report |
| M3 | `W10f-reachability-disagreement-reconciliation.md:220` | *"`huang2023` because its **PMCID status is recorded nowhere** (it is absent from `emc-site-curation.json`'s 'other seven' list)"* | **CONTRADICTED — by the LIVE TREE**, and by W10f's own declared input. `research/literature/emc-km-reachability-census-2026-08-25.json` records `"pmcid": null` with `"europe_pmc_is_open_access": "N"` for `source_id: "huang2023"` in four separate rounds (R4). Wording-level; see the caveat I attach |
| M4 | `W01f:210` | *"Verify row 8 against `retrieval.json`. **Not run** — the directory does not exist **here**"* | **STANDING but now actionable.** Correctly scoped to "here"; the live-tree absence reproduces exactly. `retrieval.json` is readable in the corpus, so the deferred verification is now performable — subject to DUPLICATE and the unpassed gate |
| M5 | `W08f-full-adjudication-envelope.md:111` | *"The only occurrences of 'leave-one-decision-out', 'extreme envelope' and 'most-inclusive rule set' anywhere in the live tree **or the frozen corpus** are inside W08e's own Next concrete action … **No prior worker has computed this**"* | **STANDING.** All three tokens: **0 corpus files**. At W08f's own HEAD `d3e9c4d8` only `W08e` carried them (`W01f` was not yet tracked; 70 reports at that commit). `W01f` now also carries two of the three, but as a **concurrent sibling in a different lane on a different object** (the obtainable band, not the interval census) — not prior work, not a refutation. Flagged so nobody records this string match as a contradiction |
| M6 | `W19g-leave-one-peakset-out.md:108` | *"**No leave-one-peakset-out analysis exists anywhere in the reports directory**"* | **CORROBORATED.** Live tree: only `W19g` itself and `W19f` (which states it was *not* computed). Corpus: **0 files** |
| M7 | `W13f-cross-file-gate-coverage.md:130` | *"**No committed code anywhere** reads a pooled artifact and the registry's `pool` flags together."* | **CORROBORATED.** **Zero** corpus-only `.py` files contain `"pool"`, and **zero** corpus-only files of any type mention `emc-clinical-registry`. The corpus supplies no counterexample |
| M8 | `W20f-probe-intersection-filter.md:361` | *"The matcher scans the Ensembl cDNA + ncRNA set, which is **not in the repository, not in the frozen corpus**, and not reachable here."* | **CORROBORATED.** 0 `.fa`/`.fasta` files in the corpus; 0 filenames matching `cdna`/`ncrna`. The two FASTA entries in `tracked-file-map.txt` are `research/manuscripts/aso/fusion-junction-aso-sequences.fasta` (present live) and `research/autonomy/lee-sequence-assay-2026-09-06/references.fasta` (in neither → **UNKNOWN**, 26 KB, far too small to be a transcriptome) |
| M9 | `W09e-views-blast-radius.md:350` | *"`systems/graph/publications.json` … has **never been audited as a whole**"* | **CORROBORATED, with a near-miss worth reading.** **Zero** corpus-only files carry `why_not_written`. Three corpus-only files reference `publications.json`; the nearest, `research/autonomy/atlas-hofvander-validation-2026-09-06/presentation/graph-update-recommendation.json`, is a **single-record** recommendation for `PUB-SURFACE-TARGETS` (`"status": "recommendation only; no graph or shared file edited"`) that quotes that record's `what_it_would_claim` — not a whole-file audit, but a lane-9 successor should read it |
| M10 | `W04d-duration-set-stability.md:169` | *"Union = 34 PMIDs. **Zero of the 34 appear anywhere in W04b's or W04c's tables.**"* | **PARTIALLY CORROBORATED / mostly UNTESTABLE.** W04d enumerates only 5 of the 34 (`19890812`, `41635359`, `151975`, `7270148`, `6402851`); all five return **0 hits** in `W04b` and `W04c`. The other 29 are not listed anywhere in the report, so the claim as a whole is untestable by literal search. My first attempt — bulk 7–8-digit extraction — produced 14 apparent overlaps, all **false positives** from W04d's separate discussion of the *committed* n=10/n=11 set; I discarded it (R5) |
| M11 | `W08g-borderline-pmid-recovery.md:119, 266`; `W13f:91` | *"`reports/W08f-*.md` **does not exist on disk at HEAD `3f5fc95`**"*; *"that path does not exist"* | **STANDING — correctly scoped, now superseded by collection.** `W08f` exists at my HEAD. W08g's `SECONDARY (transferred, unread)` marking was correct when written and remains the right label for what it actually read |
| M12 | `W08g:117` | *"**No prior worker retrieved a PMC full text for either**"* (PMIDs 38111543, 21547635) | **CORROBORATED — and W08g tested this itself against the corpus**, quoting its own `grep -rl` over `/tmp/claude-0/frozen-corpus/extracted/corpus/` with `EXIT=0`. Credit is W08g's. It is the second report after W15e to pre-emptively test itself against the corpus |
| M13 | `W01f:91` | *"Its only genuinely new content is (a) the leave-one-out table and envelopes, **which had never been computed**, and (b) one previously unnamed decision (**S-PARITY**)"* | **CORROBORATED.** `S-PARITY`: **0 corpus files**, and in the live tree only `W01f` itself |
| M14 | `W05e:303`; `W07e:258,299`; `W04d:277` | literature-availability and not-run statements (*"the paper does not exist in PubMed as of 2026-09-08"*, *"Not run — outside this dispatch's scope"*) | **NOT TESTABLE against a repository corpus.** No finding made |
| M15 | `W05e:121`; `W12d:95,202,296`; `W16d:377`; `W19e:111`; `W20f:353` | write-isolation, dispatch-scope and NOT-RUN session facts | **NOT TESTABLE** — session facts, no finding made |
| M16 | `W08f:478`; `W08h:91`; `W14d:133`; `W13f:430,451`; `W20f:244,397`; `W05f:158`; `W09e:196` | lane-, proposal- or defect-scoped statements (*"Neither has been checked for a PMC deposit"*, *"D3 is new and is a distinct sub-defect"*, *"has no committed definition, and I did not supply one"*) | **STANDING — correctly scoped.** A repository corpus cannot refute a claim about what a lane did or what a proposal contains |

**Totals over 22 new reports: 3 CONTRADICTED (M1 corpus-derived; M2 and M3 live-tree-derived), 6 CORROBORATED (M6–M9, M12, M13), 1 partially corroborated and otherwise untestable (M10), the remainder STANDING or NOT TESTABLE.**

**The W21/W21b pattern holds a third time, and now has a second edge.** Every claim scoped to *"here"*, *"at HEAD `3f5fc95`"*, *"by any permitted route"*, *"by this lane"* or *"I did not supply one"* survived (M4, M5, M11, M16). All three that broke were written as claims about the world: *"absent … from the frozen corpus"*, *"the tree's only EGA accession"*, *"recorded nowhere"*. The new edge: **two of the three are the same two defects W21b already documented, propagated into fresh reports** — the bad standing fact about the junction-source directory (M1, after W23:223) and the EGA-accession scope error (M2, after W01e:148). The corrections W21b drafted have not reached the workers.

### R2 — Falsifying evidence for M1, verbatim with path (`PRIMARY`)

```
$ ls -l /tmp/claude-0/frozen-corpus/extracted/corpus/research/autonomy/nr4a3-patient-junction-source-2026-09-07/
-r--r--r-- 1 root root  7227 README.md
-r--r--r-- 1 root root  5437 brenca-origin-gate.csv
-r--r--r-- 1 root root  6849 compare_published_calls.py
-r--r--r-- 1 root root  1573 coordinator-verification.json
-r--r--r-- 1 root root    81 delite-model-metadata.csv
-r--r--r-- 1 root root 29988 published-call-comparison.json
-r--r--r-- 1 root root  5047 recover.py
-r--r--r-- 1 root root  3870 retrieval.json
dr-xr-xr-x 2 root root  4096 sources
```

`retrieval.json`, the exact file W01f:210 defers verification to, quoted verbatim from `/tmp/claude-0/frozen-corpus/extracted/corpus/research/autonomy/nr4a3-patient-junction-source-2026-09-07/retrieval.json`:

> `{ "retrieved_utc": "2026-09-07T16:03:02.699465+00:00", "free_bytes_before": 38476955648, "raw_reads_downloaded": false, "files": [ { "path": "sources/brenca-methods.docx", "url": "https://pmc-oa-opendata.s3.amazonaws.com/PMC6766969.1/PATH-249-90-s001.docx", … "bytes": 26782, "sha256": "89b3f6382531de52ee7089cea33934c3973b0b05f41cc239d1a87e25680d6743" }, …`

**Correction for the coordinator to append (not a rewrite of W01f):**

> **Correction to `W01f-obtainable-band-stability.md` (L132).** The parenthetical *"the supporting directory is absent here and from the frozen corpus"* is half wrong. The live-tree half is right; `research/autonomy/nr4a3-patient-junction-source-2026-09-07/` **is** in the frozen corpus, as 13 corpus-only files including `README.md`, `retrieval.json`, `published-call-comparison.json`, `brenca-origin-gate.csv`, `recover.py` and `sources/{brenca,delite,urbini}-article.xml`. The correct restatement is *"absent from this checkout, present in the frozen corpus"*. Consequences, in order: (i) row 8's class is **re-derivable** from a checkable source and its `SECONDARY` marking can be revisited, and W01f:210's deferred *"Verify row 8 against `retrieval.json` — Not run"* is now performable without retrieval; (ii) **this changes nothing scientifically** — `PRJNA692081` / `SRP301712` are already recovered and remain **DUPLICATE, never novelty**; the directory's own README records that the access-and-identity gate was **not passed**, and reading its 23 ENA libraries as 23 patients is the exact inference it forbids. No cohort, independence or patient claim follows. This is the **third** report to repeat the campaign's incorrect standing fact after `W23:223` and the framing behind `W01e`; the fix belongs in the dispatch text, not in one more report.

### R3 — Falsifying evidence for M2, verbatim with path (`PRIMARY`)

```
$ grep -rhoE "EGAS[0-9]{8,12}" --exclude-dir=.git --exclude-dir=opus-capacity-campaign-20260908 . | sort | uniq -c
      3 EGAS00001000839      3 EGAS00001000855      2 EGAS00001000978
      1 EGAS00001001178      6 EGAS00001002795
```

`EGAS00001002795` is indeed Haller's, confirmed by reading the line — `research/modalities/nr4a3-fusion-targets.json:53`:

> *"NR4A3 ChIP-seq in three human AciCC tumours plus H3K27ac/H3K4me3/CTCF, processed data at Zenodo doi 10.5281/zenodo.1483691 (OPEN) and raw at EGA **EGAS00001002795** (CONTROLLED ACCESS). ⚠ AciCC carries NATIVE NR4A3 up-regulated by enhancer hijacking, NOT a fusion…"*

Four others are committed in the live tree. Three sit inside fetched article text embedded in an inputs artifact — `research/modalities/atr-hrd-sarcoma-series-inputs.json:62`:

> *"The ES whole genome sequencing data were previously deposited in the European Genome-phenome Archive (**EGAS00001000855**, **EGAS00001000839**)."* … *"deposited under EGAD00001001322, as part of a larger WGS of 560 breast cancer samples (overall project accession number **EGAS00001001178**)."*

The fourth is a curated field value, not fetched text — `research/modalities/emc-atr-vulnerability.json:384`:

> `"EGA; EGAS00001000978",`

**Correction for the coordinator to append (not a rewrite of W01f):**

> **Correction to `W01f-obtainable-band-stability.md` (row 13, L128) — live-tree-derived, NOT corpus-derived.** The parenthetical *"the tree's only EGA accession is Haller's, not EMC"* is false: five distinct EGA study accessions are committed outside the campaign reports directory. `EGAS00001002795` is Haller's AciCC study; `EGAS00001000855`, `EGAS00001000839` and `EGAS00001001178` are in `research/modalities/atr-hrd-sarcoma-series-inputs.json` (Ewing-sarcoma and breast-WGS accessions inside fetched article text); `EGAS00001000978` is a curated list entry in `research/modalities/emc-atr-vulnerability.json`. No corpus file was needed to falsify this — it is the same defect W21b recorded as N2 against `W01e:148`, propagated. **Row 13's substantive status is unaffected and stands**: none of the five is an EMC anchor, and Hofvander's TAF15 raw data remain controlled-access via EGA (an existing `CLOSED-WORK.md` closure). The wording should be narrowed to *"no committed EGA accession is an EMC-linked deposit"*, which is what W01e's D4 actually established.

### R4 — Falsifying evidence for M3, verbatim with path, and my caveat (`PRIMARY`)

From `research/literature/emc-km-reachability-census-2026-08-25.json` — a **live-tree** file (present in `git ls-files`, not corpus-only) that W10f names as its own input at `W10f:98` (*"739 lines, 16 series, 4 rounds"*):

> `{"source_id": "huang2023", "rounds": [{"slug": "km-figures-round2-2026-08-25", "pmcid": null, "europe_pmc_is_open_access": "N", …}, {"slug": "km-figures-round3-2026-08-25", "pmcid": null, "europe_pmc_is_open_access": "N", "unpaywall_is_oa": true, "unpaywall_oa_status": "bronze", "unpaywall_host_type": "publisher", … "routes": [{"route": "caller_pdf_url", "http": 403, "kind": "not-a-figure-source", "bytes": 2000, …}]}, {"slug": "km-figures-round4-browser-2026-08-25", "pmcid": null, "europe_pmc_is_open_access": "N", …}`

**Correction for the coordinator to append (not a rewrite of W10f):**

> **Correction to `W10f-reachability-disagreement-reconciliation.md` (§D, L220) — live-tree-derived, NOT corpus-derived.** *"`huang2023` because its PMCID status is recorded nowhere"* is wrong as written. `research/literature/emc-km-reachability-census-2026-08-25.json` — W10f's own declared input — records `"pmcid": null` together with `"europe_pmc_is_open_access": "N"` for `source_id: "huang2023"` across four rounds. The parenthetical *"(it is absent from `emc-site-curation.json`'s 'other seven' list)"* is accurate and is what the sentence should have said; the correct restatement is *"no **PMCID value** is recorded for `huang2023`, and it is absent from `emc-site-curation.json`'s 'other seven' list — although the reachability census records four rounds of `pmcid: null` / `is_open_access: N`."* **Flagged, not resolved:** this weakens W10f's stated rationale for choosing `huang2023` as the highest-unblocking-value query, and raises a `CLOSED-WORK.md` question about replaying a denial the census already recorded — though W10f's `convert_article_ids` call is a different mechanism from the census's `europe_pmc_is_open_access` field, so I do **not** assert it was a replay. The lane-10 owner should adjudicate. W10f's three-query result itself is untouched.

### R5 — A hit I checked and discarded (`PRIMARY`)

Testing M10 by bulk-extracting 7–8-digit integers from `W04d` and intersecting with `W04b`+`W04c` returned 14 apparent overlaps (`11917595`, `20260908`, `21941486`, `24713246`, `26125202`, `27591381`, `28360467`, `28638563`, `29657686`, `30325000`, `30985717`, `35494187`, `38440485`, `40831041`). **All are false positives.** `20260908` is a date, not a PMID; the rest come from W04d's separate analysis of the *committed* n=10/n=11 duration set, which necessarily shares PMIDs with W04b/W04c — a different set from the 34-PMID vocabulary-widening union the claim is about. Reporting that intersection as a contradiction would have been exactly the string-match error this lane exists to prevent. I discarded it and fell back to the 5 PMIDs W04d actually names.

---

## Validation evidence

All `RUN`, all read-only, all outside the repository except read-only `git`/`grep`/`sed`/`python3` against it. Environment: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, Claude Code 2.1.42, Python 3 (used only to slice two JSON files for quoting). No network.

```
$ git rev-parse HEAD                      → a87275c14897230041fde97c9965c9646474df7a  (start, exit 0)
                                          → 98a0833f1ede2cf9cef13790388260567a32e868  (end, exit 0)
$ git status --porcelain | wc -l          → 0  (start and end, exit 0)
$ git ls-tree --name-only 47aac85f… reports/ | wc -l   → 48                     exit 0
$ git ls-tree --name-only 3f5fc95d… reports/ | wc -l   → 85                     exit 0
$ git ls-tree --name-only d3e9c4d8  reports/ | wc -l   → 70                     exit 0
$ ls reports | wc -l                      → 108 (start) … 111 (end)             exit 0
$ comm -13 at-w21b-85.txt now-108.txt | wc -l          → 23                     exit 0
$ (cd corpus && find . -type f | sed 's|^\./||' | sort) | wc -l  → 5996          exit 0
$ git ls-files | sort | wc -l             → 7717                                exit 0
$ comm -23 corpus-files.txt live-files.txt | wc -l     → 2201  (corpus-only)     exit 0
$ grep -n -i -E "no prior work|does not exist|anywhere in the (tree|repo|repository|filesystem)|no committed|not in the (frozen )?corpus|for the first time|never been|…" <22 reports> | wc -l  → 39   exit 0
```

Corpus and live searches (a zero-hit `grep -rl` returns exit 1 and is reported as 0 files):

```
$ ls corpus/research/autonomy/nr4a3-patient-junction-source-2026-09-07/  → 8 files + sources/  (13 total)  exit 0
$ grep -rlI "leave-one-decision-out" corpus/                    → 0
$ grep -rlI "extreme envelope" corpus/                          → 0
$ grep -rlI "most-inclusive rule set" corpus/                   → 0
$ grep -rlI "leave-one-decision-out" --exclude-dir=.git .       → W08f, W08e, W01f   (live)
$ grep -rlI "leave-one-peakset-out" corpus/                     → 0
$ grep -rlI "leave-one-peakset-out" --exclude-dir=.git .        → W19g, W19f         (live)
$ grep -rlI "S-PARITY" corpus/                                  → 0
$ grep -rlI "S-PARITY" --exclude-dir=.git .                     → W01f only          (live)
$ <corpus-only .py files> grep -q '"pool"'                      → 0 hits
$ comm -12 <(grep -rl "emc-clinical-registry" corpus/) corpus-only.txt   → 0 files
$ comm -12 <(grep -rl "why_not_written" corpus/) corpus-only.txt         → 0 files
$ comm -12 <(grep -rl "publications.json" corpus/) corpus-only.txt       → 3 files
$ grep -icE '\.(fa|fasta)(\.gz)?$' corpus-files.txt             → 0
$ grep -icE 'cdna|ncrna' corpus-files.txt                       → 0
$ grep -iE '\.(fa|fasta)' metadata/tracked-file-map.txt         → 2 entries (one live, one in neither)
$ grep -rhoE "EGAS[0-9]{8,12}" --exclude-dir=.git --exclude-dir=opus-capacity-campaign-20260908 . | sort | uniq -c
                                                                → 5 distinct, counts in R3
$ for p in 19890812 41635359 151975 7270148 6402851; do grep -c $p W04b… W04c…; done  → 0 everywhere
```

**`PROPOSED (NOT RUN)`:** nothing. I ran no test I did not execute, authored no acceptance criterion, relaxed no guard, and ran no repository gate (`scripts/preflight.sh` not authorised by my dispatch; nothing in the tree was changed).

---

## False-positive discipline (explicit, as required)

A string match is not a claim refutation.

**Read and verified by opening the file** — these carry every CONTRADICTED verdict and the load-bearing CORROBORATED ones: `corpus/…/nr4a3-patient-junction-source-2026-09-07/` directory listing plus `retrieval.json` (first 600 bytes, quoted in R2); live `research/modalities/nr4a3-fusion-targets.json:53`, `atr-hrd-sarcoma-series-inputs.json:62` (four context windows) and `emc-atr-vulnerability.json:384`, each read as a full line with 140–160 characters of surrounding context; live `research/literature/emc-km-reachability-census-2026-08-25.json`, the `huang2023` record extracted and quoted in full across its rounds; `corpus/…/atlas-hofvander-validation-2026-09-06/presentation/graph-update-recommendation.json` (first 500 characters around its `publications.json` reference, which is how I demoted it from "audit" to "single-record recommendation"); 13 corpus `huang2023` files inspected via ±300/400-character windows filtered for `pmc`; the claim-context blocks of `W08f`, `W08g`, `W01f`, `W20f`, `W13f`, `W10f`, `W04d` read as 8–15-line windows rather than single grep lines.

**Counted but NOT read** — these support only *"no corpus-only counterexample of this kind exists"*, never a positive statement about content: the 232 corpus-only `.py` files scanned for `"pool"` by exit status alone; the corpus-only sets tested for `emc-clinical-registry` and `why_not_written` (both empty, so nothing to read); the two remaining corpus-only `publications.json` referrers (`peerj-validation-audit-2026-09-07/validation/normal-preflight-final-handoff{,-lf}.json` — judged from filename and directory as preflight handoffs, a weaker check than reading, and I flag it as such); the 5,996-entry corpus file list scanned for FASTA extensions by filename only; `research/autonomy/lee-sequence-assay-2026-09-06/references.fasta`, which I have **not** read and which is in neither source (**UNKNOWN**; my "too small to be a transcriptome" remark is an inference from its 26,686-byte size in the map, not a reading).

**Hits I explicitly declined to promote to contradictions:** (1) `W01f`'s use of *"leave-one-decision-out"* and *"extreme envelope"* against `W08f:111` — a concurrent sibling in another lane on another object, and absent from the tree at W08f's own HEAD, so not prior work (M5); (2) the 14-PMID `W04d` intersection, discarded in full as an artifact of my extraction method (R5); (3) `W08f:111`'s further clause that W08d/W08e are "now both tracked" — a collection fact, not an absence claim.

---

## Limitations

- **Scope is the 22 reports new since W21b.** W21's 48 and W21b's 36 are untouched by design; if either predecessor erred, that error is not corrected here.
- **Three reports arrived during my run and are unaudited by anyone**: `W22b`, `W24`, `W25`. `W24` is known to contain an EGAS accession string and sits in exactly the failure mode M2 documents. The reports directory grew 107 → 108 → 111 in under four minutes, so any "the collected set is N" statement is stale on arrival.
- **Claim extraction is regex-seeded and non-exhaustive** — 39 candidate lines from 17 of 22 files. Five reports produced no matching line, which means **my patterns found nothing there**, not that they contain no absence claim.
- **M10 is only 5/34 tested.** The other 29 PMIDs are not enumerated in `W04d`, so the claim as a whole is untestable by literal search and I did not test it.
- **M3 is a judgement about wording, and I say so.** Whether `"pmcid": null` constitutes "PMCID status recorded" is arguable; I judged four rounds of `null` alongside an explicit `europe_pmc_is_open_access: "N"` to be a recorded status. A reader who disagrees should downgrade M3 to STANDING. I did **not** assert that W10f replayed a denied route.
- **Absence from the snapshot is not repository-wide absence.** Every CORROBORATED verdict means only *"also absent from this selected snapshot of 5,996 files"*. Quoting `snapshot-provenance.json`: *"Absence is not evidence of repository-wide absence, source novelty or access permission."*
- **The corpus is not a Git checkout and I verified no checksum myself** — I relied entirely on the coordinator's verification in `CORPUS-CONTEXT.md`, and did not test base `93b75888…` for local presence this run.
- **Corpus-only files are prior *repository work*, not new *source material*** — `"no_new_source_material": true`, `"no_source_fetch": true`, `"no_scientific_acceptance": true`.
- **M2 and M3 are not corpus findings** and must not be recorded as such; only M1 is corpus-derived.
- **No clinical claim.** This is a provenance audit. Nothing here bears on EMC biology, NR4A3 fusion behaviour, degrader efficacy, safety, selectivity, therapeutic window or clinical readiness, and no result admits any cohort, patient or independence claim. The Brenca accessions remain **DUPLICATE**; the junction-source directory's access-and-identity gate remains **not passed**, and its 23 ENA libraries are **not** 23 patients.
- **No content-policy refusal occurred in this run.** Nothing here reviews, recreates, reroutes or reframes the blocked NR4A Perspective.

---

## Stop condition

Set up front: *all three report sets stated by filename with neither predecessor's set re-audited; every explicit novelty/absence claim in the new reports extracted with `file:line` and tested by literal search against both the corpus and the live tree; the falsifying source named for each contradiction; verbatim evidence and a correct restatement drafted for each; false-positive discipline stated including the hits I only counted.*

**MET.** Sets stated: 48 (W21) / 36 (W21b) / 23 new, 22 audited and one excluded with reason. 39 claim lines classified into 16 clusters: **3 CONTRADICTED** (M1 corpus-derived; M2, M3 live-tree-derived and flagged as such), **6 CORROBORATED**, **1 partially corroborated / otherwise untestable**, the rest STANDING or NOT TESTABLE. Three corrections drafted verbatim for the coordinator to append; no report rewritten. Two of the three contradictions are W21b's already-drafted corrections propagating into new reports because those corrections have not reached workers. Returning now.

---

## Tool-call and wall-clock count actually used

**24 tool calls**, all `Bash`. **Wall clock 3 min 44 s measured** to my end stamp (`03:04:06Z` → `03:07:50Z`), plus context reading before the first timestamp and report drafting after the last call. Well inside the ~40-call / ~40-minute self-observed target.

---

## Next concrete action

**Fix the campaign's dispatch text before dispatching anyone else, then append the three corrections.** The dispatch-borne standing fact that `research/autonomy/nr4a3-patient-junction-source-2026-09-07/` is absent from the frozen corpus has now produced a false absence claim in **three separate reports** (`W23:223`, the framing behind `W01e`, and now `W01f:132`), and the EGA-accession scope error has produced two (`W01e:148`, `W01f:128`). Appending corrections downstream does not stop the source. Both edits are coordinator writes needing no retrieval, no network and no new analysis; the corrections are drafted verbatim in R2, R3 and R4.

**Second, cheap and bounded:** audit `W22b`, `W24` and `W25`, which arrived during my run and which no pass has covered — `W24` in particular, since it carries an EGAS accession string and is a "repair routing index", exactly the artifact that would propagate M2 further.

**Explicitly not a successor, and I recommend against it:** re-auditing W21's or W21b's sets (a repeat), and treating the now-readable junction-source `retrieval.json` as anything more than a provenance record — the accessions are already recovered (**DUPLICATE**), the directory's README records that its access-and-identity gate was **not passed**, and reading 23 ENA libraries as 23 patients is the exact inference it forbids.
