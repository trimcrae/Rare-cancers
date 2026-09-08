<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:24:44Z UTC
     agent id a4836b5beb1f9182c ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a4836b5beb1f9182c.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

## Worker

**W21d** — corpus-differential lane, fourth pass, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable observed names a served model. The coordinator must extract the actual per-child runtime model from the transcript; do not treat this line as observed fact.

`date -u` at **start**: `Tue Sep  8 03:17:25 UTC 2026`
`date -u` at **end**: `Tue Sep  8 03:20:18 UTC 2026` (report drafting continued past this stamp; no tool call after it touched anything)

| Point | `git rev-parse HEAD` | `git status --porcelain \| wc -l` |
|---|---|---|
| start (**my audit set is pinned here**) | `c81236b90c7905caa2e75a57b332ad33f2c10d02` | 0 |
| end | `84f02dae1809ae050e40254f06310ed849982527` | 0 |

HEAD moved once under me. I wrote nothing into `/home/user/Rare-cancers` and nothing under `/tmp/claude-0/frozen-corpus/`. All scratch under `/tmp/claude-0/w21d/`. No git write operation, no network, no retrieval, no MCP call, no paid API, no GPU, no `preflight.sh`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (verbatim; the long proxy lists abridged as marked, nothing else altered):

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

**Mid-run scope narrowing, received from the coordinator and applied immediately:** `W25-gse243553-candidate-merit.md` is **HELD/EXCLUDED**. I did not read it, extracted no claim from it, and tested no statement of it. Reason as given: the scientific owner has placed a hold pending an unresolved primary-source verification, and a separate safety event of UNKNOWN scope is recorded against a related continuation; auditing it could be construed as continuing that work by another route. It is counted below as HELD/EXCLUDED, not as audited and not as unaudited-and-available. The message arrived after my defect-recurrence sweep had already run; that sweep's grep did include `W25` in its file list, and its output shows **zero** matching lines from `W25` — no `W25` content entered this report, and no `W25` claim was extracted, read or tested.

---

## Question

**Do the campaign reports collected since W21c pinned its set carry any novelty or absence claim that the frozen corpus or the live tree contradicts — and, decisively, do the two already-documented propagating defects appear again in them?**

Open because W21c pinned at `a87275c1…` with 108 reports and explicitly named `W22b`, `W24` and `W25` as arriving during its run and untested by anyone; the directory has since grown to 126 files / 109 report IDs. The recurrence question is open because W21b drafted a correction for the EGA-accession scope error and W21c drafted three more, and nobody has measured whether the dispatch-text fix W21c demanded actually stopped the propagation.

---

## Prior-work check

**All four report sets, by filename, with the three predecessors re-audited by nobody here.**

```
$ ls .../reports | sort | wc -l                                  → 126 files
$ sed -E 's/^(W[0-9]+[a-z]?)-.*/\1/' | sort -u | wc -l           → 109 report IDs
$ comm -13 prior_ids.txt now_ids.txt                             → 17 IDs (my candidate set)
```

- **Set 1 — `W21-corpus-differential-audit.md`, 48 reports.** Not re-audited; W21's verdicts stand.
- **Set 2 — `W21b-corpus-differential-second-pass.md`, 36 reports.** Not re-audited; W21b's verdicts stand.
- **Set 3 — `W21c-corpus-differential-third-pass.md`, 22 reports.** Not re-audited; W21c's verdicts stand. **I did not redraft any of W21c's three corrections** (its R2 on `W01f:132`, R3 on `W01f:128`, R4 on `W10f:220`); they remain W21c's to append verbatim.
- **Set 4 — mine, 17 candidate IDs, 16 audited, 1 HELD:**
`W01g-transcriptome-wide-criterion.md`, `W02f-fibro-ecm-decomposition.md`, `W02g-gene-set-matched-null.md`, `W04e-delay-attribution-route.md`, `W05g-schema-level-independence-check.md`, `W06f-coherent-share-readout.md`, `W07f-emc-only-cohort-full-texts.md`, `W09f-publications-false-absence-audit.md`, `W12e-subprocess-env-residual.md`, `W16e-regeneration-identity-check.md`, `W17i-aggregate-block-recovery.md`, `W18b-two-channel-selection-model.md`, `W19h-fus-fev-scoping-arm.md`, `W20g-published-denominator-consistency.md`, `W22b-final-provenance-ledger.md`, `W24-repair-routing-index.md`; plus **`W25-gse243553-candidate-merit.md` — HELD/EXCLUDED by coordinator instruction.**

The set difference is exact: `comm -23 prior_ids.txt now_ids.txt` is empty, so no ID any predecessor claimed has vanished, and every ID now present is covered by exactly one of the four sets.

`CLOSED-WORK.md` read in full. Not replayed, re-reviewed or relabelled: the blocked NR4A Perspective refusal — I did not approach, relabel or reframe it under any label, agent or framing; the user-rejected registry ICD-O paper; the Davis, Hofvander, Brenca, promoter-transfer and inverse-bounds closures; every unrecovered source (I fetched nothing and used no network of any kind); the lane-11 source-index bundle, on which I tested absence claims only and proposed no change. **`PRJNA692081` / `SRP301712` are ALREADY RECOVERED → DUPLICATE, never novelty**; I make no accession-derived finding. I make **no cohort, independence or patient claim**; the junction-source directory's own access-and-identity gate was **not passed** and its ENA libraries are **not** patients. There is no wet lab and I make no clinical claim.

---

## Method / inputs

- **Live checkout** `/home/user/Rare-cancers`, read-only (`git ls-files`, `git rev-parse`, `git status`, `grep`, `sed`, `find`, `ls`). **Pinned at `c81236b9…`**; every count below is at that HEAD unless stated.
- **Frozen corpus** `/tmp/claude-0/frozen-corpus/extracted/corpus/` — the **corrected repository-relative root** given in my dispatch. Read **in place**, never copied, never overlaid. I confirmed the root by listing it: it contains `AGENTS.md`, `CLAUDE.md`, `README.md`, `research/`, `scripts/`, `systems/` — i.e. it *is* the repository-relative root, and `…/extracted/` is not.
- **Scratch** `/tmp/claude-0/w21d/` — `now.txt`, `prior_ids.txt`, `now_ids.txt`, `claims.txt`.
- **Claim pool:** one regex sweep over the 16 audited reports → **50 candidate lines in 14 files**; two reports (`W07f`, `W18b`) produced no matching line.
- **No network, no retrieval, no external source, no repository gate run, no report rewritten.** I route; the coordinator writes.

---

## Result

### R0 — THE DECISION-RELEVANT NUMBER: recurrence of the two known propagating defects

Reported separately, as dispatched. Sweep run over all 16 audited reports (plus `W25`, which returned zero lines):

```
$ grep -n -i "junction-source\|nr4a3-patient-junction" <16 reports>     → 5 lines, 2 files
$ grep -n -i "EGAS[0-9]\|EGA accession\|only EGA\|European Genome" <16> → 1 line, 1 file
```

| Defect | Recurrences as a **fresh false claim** | Detail |
|---|---|---|
| **A — "the junction-source directory is absent from the frozen corpus"** | **0 / 16** | **The dispatch fix worked.** `W24:210` states it **correctly**: *"Absent from the live checkout at every HEAD this campaign has read; **PRESENT in the frozen corpus as 13 corpus-only files**"*. `W24:239` goes further and records the correction of `W23:223` as adjudicated fact, naming the cause: *"`WAVE-LOG.md` ~02:58Z records the coordinator's own correction: the path was `…/extracted/corpus/`, not `…/extracted/`."* `W01g:90` is **correctly scoped** — *"confirms the directory is absent from **this checkout**, as the dispatch states. I did not read the frozen corpus this run; nothing below depends on it."* |
| **B — the EGA-accession scope error** | **0 / 16 as a claim; 1 / 16 as a mis-transcribed count** | No report re-asserts *"the tree's only EGA accession is Haller's"*. `W24:240` correctly logs it as **CONTRADICTED**. But its transcription of the correction is numerically wrong (**R1/C-B below**), so the defect has changed shape rather than fully stopped. |

**Read this as: the corrective dispatch text stopped the false absence claim outright, and stopped the false EGA claim outright, but the correction itself is now propagating with an arithmetic slip in it.** Correcting downstream is working; the remaining leak is the accuracy of the correction text, not the workers.

### R1 — Verdict table, 16 audited reports (`PRIMARY` unless marked)

| # | Report `file:line` | Claim (quoted, abridged) | Verdict / falsifying source |
|---|---|---|---|
| **C-B** | `W24-repair-routing-index.md:240` | C5's resolution column: *"`W21b:N2`: **six** distinct EGAS accessions — **four in the live tree**, two corpus-only"* | **CONTRADICTED — by the LIVE TREE and the CORPUS jointly.** Measured: **seven** distinct EGAS accessions, **five** in the live tree outside the campaign reports directory, **two** corpus-only (R2). W24 marks this row *"Not verified by me"*, which is honest; the error is inherited from `W21b:145`'s table cell, whose own correction draft at `W21b:184` is arithmetically right. **W24's routing verdict — that `W01e:148` is contradicted — is correct and stands.** Only the count is wrong |
| C1 | `W24:146`, `:229` | *"`research/tools/` **does not exist** in the live tree"*; *"`find` shows it only inside `inputs/source-index/`"* | **CORROBORATED.** `find` at my HEAD returns exactly one `tools` directory: `./research/autonomy/opus-capacity-campaign-20260908/inputs/source-index/research/tools`. **Also absent from the corpus** (`ls: cannot access …/corpus/research/tools`). The path-divergence flag DBW24 raises against R13 is real |
| C2 | `W24:230` | *"`scripts/source_reuse_index.py`, `scripts/tests/test_source_reuse_index.py` — `ls` exit 2"* | **CORROBORATED.** Absent from the live tree **and** from the corpus |
| C3 | `W24:226` | *"Any tracked `.bed` file anywhere in the tree"* listed as NONEXISTENT | **CORROBORATED.** `git ls-files \| grep -ciE '\.bed(\.gz)?$'` → **0**; corpus `find -iname '*.bed*'` → **0** |
| C4 | `W24:210, :239` | junction-source directory present in the corpus as 13 files | **CORROBORATED** (and see R0). Marked `SECONDARY — I did not read the corpus`; I read it, and the transcription is accurate |
| C5 | `W20g-published-denominator-consistency.md:100` | *"**`212101` and `211362` appear nowhere in the tree**"* | **CORROBORATED.** My first bulk grep returned 2 files for each — **all false positives**, every one a substring inside a longer number (R3). Discarded; the claim holds. Corpus: **0** |
| C6 | `W02f-fibro-ecm-decomposition.md:102` | *"`herfindahl\|HHI_gene\|HHI_sample` returns **exactly one file**… exists nowhere else in the tree"* | **CORROBORATED at its own HEAD, superseded by collection.** Now three files carry it — `W02e`, `W02f` itself, and `W02g`, its own declared successor. **Zero** outside the campaign reports directory; **zero** in the corpus. The two new carriers are a self-reference and a sibling built on it, not prior work — I decline to promote this to a contradiction |
| C7 | `W02g-gene-set-matched-null.md:119` | *"`R_gene` … **exactly one file**: `…/W02f-…`. **Nowhere else in the tree.**"* | **CORROBORATED at its own HEAD, superseded by collection.** Now `W02f` **and `W02g` itself**. Zero outside the campaign reports; **zero** in the corpus |
| C8 | `W06f-coherent-share-readout.md:91` | *"The field name [`smallest_coherent_share`] exists **nowhere else in the corpus**."* | **CORROBORATED.** **Zero** files in the frozen corpus. Live: only `W06e` (its predecessor's nomination) and `W06f` itself; **zero** outside the campaign reports |
| C9 | `W04e-delay-attribution-route.md:93` | *"PMID 19890812 … appears **nowhere else in the tracked tree and nowhere in the frozen corpus**"* | **CORROBORATED.** Zero live outside the campaign reports; **zero** corpus files. W04e names the corpus root correctly in its own text |
| C10 | `W09f-publications-false-absence-audit.md:108` | *"⚠ **One correction to the dispatch's own arithmetic.** … The file holds **33 records carrying 41 such fields** — 33 `what_it_would_claim` and 8 `why_not_written`. **Forty, not thirty-two**, had never been audited."* | **CORROBORATED, after I nearly recorded it as wrong.** My first count (`grep -c`) returned **34** `what_it_would_claim`, apparently contradicting W09f. Reading the extra line showed it is `publications.json:119`, a **`why_not_written` value whose prose quotes the field name** (R4). Key-position count: `^\s*"what_it_would_claim":` → **33**; `^\s*"why_not_written":` → **8**. W09f is exactly right |
| C11 | `W12e-subprocess-env-residual.md:105` | *"**zero** code, script or workflow hit for any of the three interpreter-encoding variables **anywhere in the tree** outside this campaign's own report text"* | **STANDING — correctly scoped, with a corpus near-miss the lane should see.** Live outside the campaign reports: **0**, exactly as W12e reports. The corpus holds **one** file, **corpus-only**: `research/autonomy/peerj-validation-audit-2026-09-07/final-handoff/package-ready.json:304-305` → `"PYTHONUTF8": "1"`, `"PYTHONIOENCODING": "utf-8"`. It is a JSON handoff record, **not** code, a script or a workflow, so it does not meet W12e's own stated predicate and is **not** a contradiction — but it shows the repository at snapshot base `93b…` did once record those variables being set (R5) |
| C12 | `W17i-aggregate-block-recovery.md:163` | *"The module, returned inline (**authored nowhere in the tree**)"* | **CORROBORATED.** `git ls-files \| grep -c test_reconstructed_panel_and_set_score_blocks` → **0**. Consistent with its own `PROPOSED (NOT RUN)` marking of landing the file |
| C13 | `W22b-final-provenance-ledger.md:103, :131` | *"This record is **operational provenance only**. It is **NOT a scientific acceptance gate**, it bears on no report's correctness… Every `quoted_not_verified` string is a verbatim quotation of report text; **I executed none of them and verified none of them**."* | **STANDING — and this is the right self-limitation.** A ledger that declares its own strings unverified makes no absence or novelty claim for a corpus to refute. `W22b` produced no other candidate line. Nothing in it should be cited as acceptance |
| C14 | `W24:282` | *"**I did not read 65 of the 92 reports.** Any repair… living only in a section my greps did not match is absent from this index, and **its absence is UNKNOWN, not evidence it does not exist**."* | **STANDING — correctly scoped, and load-bearing.** This is the honest limitation that makes the rest of `W24` safe to route from. It also means `W24` is an **index, not a census**, and must not be cited as one |
| C15 | `W24:236` (C1), `:241` (C6), `:242` (C7), `:244` (C9), `:245` (C10) | transcriptions of W08b's, W21b's and W21's earlier verdicts | **NOT RE-TESTED BY ME, deliberately.** Each is a faithful pointer into `W21`, `W21b` or `W08b`, all of which are in predecessors' pinned sets. Re-testing them would be re-auditing sets 1–2. I checked only that each row **names its source and marks itself unverified**, which every one does. `W24:245`'s *"Resolved by time, not by error"* on `W13e` is the same superseded-by-collection pattern as C6/C7 and is correctly labelled |
| C16 | `W01g:186, :194, :279`; `W02f:246`; `W02g:107`; `W05g:80`; `W16e:111, :169, :171`; `W19h:485`; `W20g:219`; `W09f:158-269, :358` | criterion-definition, arithmetic-internal, lane-scoped and literature-availability statements | **NOT TESTABLE by literal search against a repository corpus / STANDING.** Two sub-classes: (a) statements about what a *definition* would exclude or what a *lane* did — a corpus cannot refute these; (b) `W09f`'s own OVER-SCOPED/UNVERIFIABLE gradings, which are already an evidence comparison inside `publications.json` and which `W09f:358` correctly limits: *"'FALSE' here means a committed counter-record exists in this tree. It does not mean I searched the literature."* No finding made |

**Totals over 16 audited reports: 1 CONTRADICTED (C-B, live-tree + corpus derived), 11 CORROBORATED (C1–C10, C12), 3 STANDING (C11, C13, C14), 1 deliberately not re-tested (C15), the remainder NOT TESTABLE (C16). `W25` HELD/EXCLUDED, 0 claims extracted.**

**The W21/W21b/W21c pattern holds a fourth time and the sample is now large.** Every claim scoped to *"this checkout"*, *"at this HEAD"*, *"by any permitted route"*, *"I did not read the corpus"* survived (C4, C11, C13, C14, and C6/C7 which were true when written). The single break is again a statement written about the world — a bare count with no scope on it. **The new observation is that the world-scoped claims have nearly disappeared from this cohort**: 1 contradiction in 16 reports, against 3 in 22 (W21c) and 3 in 36 (W21b), and the one that broke is a *transcription of a correction*, not an original assertion.

### R2 — Falsifying evidence for C-B, verbatim with paths (`PRIMARY`)

```
$ grep -rhoE "EGAS[0-9]{8,12}" --exclude-dir=.git --exclude-dir=opus-capacity-campaign-20260908 .  | sort | uniq -c
      3 EGAS00001000839      3 EGAS00001000855      2 EGAS00001000978
      1 EGAS00001001178      6 EGAS00001002795          → 5 distinct in the LIVE TREE

$ grep -rhoE "EGAS[0-9]{8,12}" /tmp/claude-0/frozen-corpus/extracted/corpus/ | sort | uniq -c
      3 EGAS00001000839      3 EGAS00001000855      1 EGAS00001000978
      1 EGAS00001001178      6 EGAS00001002795      3 EGAS00001002920
      1 EGAS50000000393                                 → 7 distinct in the CORPUS
```

Per-accession live presence, tested file by file (`[ -f live/<path> ]` on each corpus file that carries it):

| Accession | Where | Live? |
|---|---|---|
| `EGAS00001002795` (Haller, AciCC) | `research/modalities/nr4a3-fusion-targets.json` and 4 more | **LIVE** |
| `EGAS00001000839`, `EGAS00001000855`, `EGAS00001001178` | `research/modalities/atr-hrd-sarcoma-series-inputs.json` | **LIVE** |
| `EGAS00001000978` | `research/modalities/emc-atr-vulnerability.json` | **LIVE** |
| `EGAS00001002920` | `research/autonomy/zullow-emc-source-2026-09-06/{README.md, README-original.md.txt, coordinator_verify.py}` | **CORPUS-ONLY** |
| `EGAS50000000393` | `research/autonomy/next-paper-2026-09-07/native-cell-source-gate.json` | **CORPUS-ONLY** |

**5 live + 2 corpus-only = 7 distinct**, not "six … four in the live tree, two corpus-only". The slip is one accession short on the live-tree side and therefore one short on the total.

**Correction for the coordinator to append (not a rewrite of W24, and not a redraft of W21b's or W21c's corrections):**

> **Correction to `W24-repair-routing-index.md` (row C5, L240) — a count, not a verdict.** The resolution column reads *"`W21b:N2`: **six** distinct EGAS accessions — four in the **live tree**, two corpus-only"*. Measured at HEAD `c81236b9…` against the frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/corpus/`: there are **seven** distinct EGA study accessions — **five in the live tree** outside this campaign's reports directory (`EGAS00001002795`, `EGAS00001000839`, `EGAS00001000855`, `EGAS00001001178`, `EGAS00001000978`) and **two corpus-only** (`EGAS00001002920` in `zullow-emc-source-2026-09-06/`, `EGAS50000000393` in `next-paper-2026-09-07/native-cell-source-gate.json`). The smallest correct restatement is *"seven distinct EGAS accessions — five in the live tree, two corpus-only"*. **C5's routing verdict is unaffected and stands**: `W01e:148` is contradicted, and W24 correctly marks the row *"Not verified by me."* The slip originates upstream in `W21b:145`'s table cell, whose own correction draft at `W21b:184` states it correctly (*"Four **further** EGA accessions … two more are corpus-only"*, i.e. four beyond Haller's = five); `W24` transcribed the cell rather than the draft. **Nothing scientific turns on this.** None of the seven is an EMC-linked deposit: `EGAS00001002795` is Haller's AciCC study (native NR4A3, not a fusion), `EGAS00001002920` is a synovial/epithelioid sarcoma study, `EGAS50000000393` is recorded with *"no EMC-specific identity recovered"*, and Hofvander's TAF15 raw data remain controlled-access via EGA per `CLOSED-WORK.md`. No cohort, independence or patient claim follows, and the fix belongs in one appended line, not in a new review round.

### R3 — A contradiction I found, read, and discarded (`PRIMARY`)

`W20g:100` claims `212101` and `211362` *"appear nowhere in the tree"*. My literal grep returned **2 files for each**, which would have been a contradiction. I read every hit:

```
research/modalities/emc-ret-cistrome-inputs.json:4006755:     211362074,
research/modalities/emc-ret-cistrome-inputs.json:1328138:      67211362,
results/nr4a3-metad-r3/ckpt/COLVAR:16379:  16378.000000 0.777242 131.212101
results/nr4a3-metad-r3/ckpt/HILLS:9561:    9558  0.587221210106556  0.03 ...
results/nr4a3-metad-r1/ckpt/HILLS:13612:  13609  0.8402042581291815  0.03  0.007120211362115539  10
```

**Every hit is a substring inside a longer integer or a floating-point mantissa** — cistrome genomic coordinates and metadynamics checkpoint values. Not one is the denominator `212,101` or `211,362`. **Discarded in full; W20g's claim is CORROBORATED.** This is the same class of error as W21c's R5 and is exactly what this lane exists to catch.

### R4 — A second discarded contradiction (`PRIMARY`)

`W09f:108` corrects the dispatch's arithmetic to *"33 `what_it_would_claim` and 8 `why_not_written`"*. `grep -c 'what_it_would_claim' systems/graph/publications.json` → **34**, apparently one too many. I read the extra line rather than reporting it:

> `systems/graph/publications.json:119` — `"why_not_written": "⚠ Superseded, retained (rule 1.2): \"Its four contributing routes are registered and their evidence is cited but not yet extracted…`

The literal string `what_it_would_claim` occurs **inside that `why_not_written` value's prose**, not as a key. Counting key positions only: `grep -cE '^\s*"what_it_would_claim":'` → **33**, `grep -cE '^\s*"why_not_written":'` → **8**. **W09f is exactly right and my count was the error.**

### R5 — The corpus near-miss behind C11, verbatim (`PRIMARY`, flagged not asserted)

```
$ grep -rlIE "PYTHONUTF8|PYTHONIOENCODING|PYTHONCOERCECLOCALE" /tmp/claude-0/frozen-corpus/extracted/corpus/
research/autonomy/peerj-validation-audit-2026-09-07/final-handoff/package-ready.json     [CORPUS-ONLY]
:304:      "PYTHONUTF8": "1",
:305:      "PYTHONIOENCODING": "utf-8"
```

**Not a contradiction of `W12e:105`**, whose grep is explicitly restricted to `*.py`/`*.sh`/`*.yml`. It is a note for the lane-12 owner: at snapshot base `93b75888…` a validation handoff package did record those two variables being set, which is prior *repository work* on the same subject, not new source material and not evidence the defect census is wrong.

---

## Validation evidence

All `RUN`. All read-only. All outside the repository except read-only `git`/`grep`/`sed`/`find`/`ls` against it. Environment: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, Claude Code 2.1.42, GNU grep/sed/find, bash. **No network of any kind.**

```
$ date -u                                 → Tue Sep  8 03:17:25 UTC 2026 (start)  exit 0
                                          → Tue Sep  8 03:20:18 UTC 2026 (end)    exit 0
$ git rev-parse HEAD                      → c81236b90c7905caa2e75a57b332ad33f2c10d02 (start) exit 0
                                          → 84f02dae1809ae050e40254f06310ed849982527 (end)   exit 0
$ git status --porcelain | wc -l          → 0 (start), 0 (end)                     exit 0
$ ls .../reports | sort | wc -l           → 126                                    exit 0
$ sed -E 's/^(W[0-9]+[a-z]?)-.*/\1/' | sort -u | wc -l  → 109                      exit 0
$ comm -13 prior_ids.txt now_ids.txt      → 17 IDs                                 exit 0
$ comm -23 prior_ids.txt now_ids.txt      → (empty; no predecessor ID missing)      exit 0
$ ls /tmp/claude-0/frozen-corpus/extracted/corpus/   → AGENTS.md CLAUDE.md README.md research scripts systems   exit 0
$ grep -n -i "junction-source|nr4a3-patient-junction" <16 reports>  → 5 lines, 2 files   exit 0
$ grep -n -i "EGAS[0-9]|EGA accession|only EGA|European Genome" <16> → 1 line, 1 file    exit 0
$ grep -n -i -E "<25-alternative absence/novelty regex>" <16 reports> | wc -l  → 50      exit 0
$ grep -rhoE "EGAS[0-9]{8,12}" --exclude-dir=.git --exclude-dir=opus-…-20260908 . | sort | uniq -c  → 5 distinct   exit 0
$ grep -rhoE "EGAS[0-9]{8,12}" corpus/ | sort | uniq -c              → 7 distinct        exit 0
$ grep -rlE "EGAS00001002920" corpus/  → 3 files, all CORPUS-ONLY by [ -f ] test         exit 0
$ grep -rlE "EGAS50000000393" corpus/  → 1 file,  CORPUS-ONLY by [ -f ] test             exit 0
$ find . -path ./.git -prune -o -type d -name tools -print  → 1 (inputs/source-index/…)  exit 0
$ ls corpus/research/tools                → No such file or directory                    exit 2
$ ls scripts/source_reuse_index.py         → No such file or directory                    exit 2
$ ls corpus/scripts/source_reuse_index.py  → No such file or directory                    exit 2
$ git ls-files | grep -ciE '\.bed(\.gz)?$' → 0                                            exit 1
$ find corpus/ -iname '*.bed' -o -iname '*.bed.gz' | wc -l  → 0                           exit 0
$ grep -rlIE "herfindahl|HHI_gene|HHI_sample" <live excl campaign> → 0 ; corpus → 0       exit 1
$ grep -rlIE "herfindahl|HHI_gene|HHI_sample" <live incl campaign> → W02e, W02f, W02g     exit 0
$ grep -rlI "R_gene" <live excl campaign> → 0 ; corpus → 0 ; incl campaign → W02f, W02g   exit 1/0
$ grep -rlI "smallest_coherent_share" <live excl campaign> → 0 ; corpus → 0 ; incl → W06e, W06f  exit 1/0
$ grep -rlI "19890812" <live excl campaign> → 0 ; corpus → 0                              exit 1
$ grep -rlIE "PYTHONUTF8|PYTHONIOENCODING|PYTHONCOERCECLOCALE" <live excl campaign> → 0 ; corpus → 1  exit 1/0
$ grep -rnI -e 212101 -e 211362 <live excl campaign> → 13 lines, ALL substring FPs (R3)   exit 0
$ grep -cE '^\s*"what_it_would_claim":' systems/graph/publications.json  → 33             exit 0
$ grep -cE '^\s*"why_not_written":'     systems/graph/publications.json  → 8              exit 0
$ git ls-files | grep -c 'test_reconstructed_panel_and_set_score_blocks' → 0              exit 1
```

A zero-hit `grep -rl` returns exit 1 and is reported as 0 files throughout.

**`PROPOSED (NOT RUN)`:** nothing. I executed every test I report, authored no acceptance criterion, relaxed no guard, changed nothing in the tree, and ran no repository gate (`scripts/preflight.sh` is not authorised by my dispatch and nothing was changed that would need it).

---

## False-positive discipline

A string match is not a claim refutation. Stated explicitly, as dispatched.

**Read by opening the file — these carry the one CONTRADICTED verdict and every load-bearing CORROBORATED one:**
`W24-repair-routing-index.md` lines 146, 210, 214–230, 236–245, 282–284, read as multi-line windows, not grep lines — this is how I established that C4 states the junction-source fact *correctly* and that C5's error is a count inside an otherwise-correct row; `W21b-corpus-differential-second-pass.md` lines 145, 165–184, 245–246, read to locate where the "six/four" slip originates and to confirm `W21b:184`'s draft is right (**this is a read of one cell for provenance, not a re-audit of W21b's set — W21b's 36 verdicts are untouched**); live `research/modalities/nr4a3-fusion-targets.json`, `atr-hrd-sarcoma-series-inputs.json`, `emc-atr-vulnerability.json` — accession lines located and each carrying file tested for live presence individually; corpus `zullow-emc-source-2026-09-06/README.md` and `next-paper-2026-09-07/native-cell-source-gate.json` located as the two corpus-only carriers; corpus `peerj-validation-audit-2026-09-07/final-handoff/package-ready.json:304-305` read as the actual key/value pair (R5); live `systems/graph/publications.json:119` read in full (R4) — this single read is what stopped me reporting `W09f` as wrong; all 13 live `212101`/`211362` hit lines read individually (R3); the claim-context blocks of `W06f`, `W12e`, `W17i`, `W20g`, `W01g`, `W02f`, `W02g`, `W04e` read as 8–15-line windows.

**Counted but NOT read — these support only "no counterexample of this kind exists here", never a positive statement about content:** the corpus and live file *lists* scanned for `.bed` by filename/extension only; the `herfindahl`/`R_gene`/`smallest_coherent_share`/`19890812` sweeps, which returned **zero** files outside the campaign directory, so there was nothing to read; the 50-line claim pool itself, of which I promoted 14 clusters and left the rest as NOT TESTABLE without opening every source line; `W05g`, `W16e`, `W18b`, `W19h`, `W07f`, `W22b` — I read only their matched claim lines and their surrounding context, **not** the full reports.

**Hits I explicitly declined to promote to contradictions:** (1) the 13 `212101`/`211362` substring hits (R3) — all inside longer numbers; (2) my `grep -c` of `what_it_would_claim` returning 34 against `W09f`'s 33 (R4) — the extra match is prose inside a `why_not_written` value; (3) the corpus `PYTHONUTF8`/`PYTHONIOENCODING` file against `W12e:105` (R5) — a JSON handoff, outside W12e's own stated `.py`/`.sh`/`.yml` predicate; (4) `W02f`, `W02g` and `W06f` now appearing in searches their own claims say return one file (C6, C7, C8) — self-reference and declared successors collected after the claim was written, the same superseded-by-collection pattern W21c flagged as M5 and W24 labels *"Resolved by time, not by error"*.

---

## Limitations

- **Scope is the 16 reports collected since W21c pinned its set, minus W25.** W21's 48, W21b's 36 and W21c's 22 are untouched by design; if any predecessor erred, that error is not corrected here. My one read into `W21b:145/184` was to trace C-B's provenance and is not a re-audit.
- **`W25` is HELD/EXCLUDED** on coordinator instruction. Its claims are **not** audited, **not** cleared, and **not** available for audit. Nothing here should be read as any statement about `W25`'s correctness in either direction.
- **Claim extraction is regex-seeded and non-exhaustive** — 50 candidate lines from 14 of 16 files. Two reports (`W07f`, `W18b`) produced no matching line, which means **my patterns found nothing there**, not that they contain no absence claim.
- **`W24` is an index, not a census, by its own statement** (`W24:282`: *"I did not read 65 of the 92 reports"*). My corroborations of C1–C4 confirm the rows `W24` wrote; they say nothing about what `W24` did not index.
- **`W24`'s C15 rows are transcriptions I deliberately did not re-test**, because their sources sit in predecessors' pinned sets. If `W21`, `W21b` or `W08b` erred, `W24` inherits it and I would not have caught it — C-B is the one case where I did, and only because it was a bare count I could measure without re-auditing anything.
- **Absence from the snapshot is not repository-wide absence**, and is never evidence of source novelty or of access permission. Every CORROBORATED verdict means only *"also absent from this selected snapshot of 5,996 files"*. Quoting `snapshot-provenance.json`: *"Absence is not evidence of repository-wide absence, source novelty or access permission."*
- **The corpus is not a Git checkout and I verified no checksum myself** — I relied entirely on the coordinator's verification in `CORPUS-CONTEXT.md`. I did not check out or inspect base `93b75888…`.
- **Corpus-only files are prior *repository work*, not new *source material*** — `"no_new_source_material": true`, `"no_source_fetch": true`, `"no_scientific_acceptance": true`.
- **C-B is a live-tree-plus-corpus finding, not a corpus finding**, and must not be recorded as the corpus contradicting anything on its own.
- **HEAD moved once during my run** (`c81236b9…` → `84f02da…`). My audit set and every count are pinned to `c81236b9…`; any "the collected set is N" statement here is stale on arrival.
- **No clinical claim.** This is a provenance audit. Nothing here bears on EMC biology, NR4A3 fusion behaviour, degrader efficacy, safety, selectivity, therapeutic window or clinical readiness, and there is no wet lab. No result admits any cohort, independence or patient claim. `PRJNA692081` / `SRP301712` remain **DUPLICATE, never novelty**; the junction-source directory's access-and-identity gate remains **not passed** and its ENA libraries are **not** patients.
- **No content-policy refusal occurred in this run.** Nothing here reviews, recreates, reroutes, relabels or reframes the blocked NR4A Perspective.

---

## Stop condition

Set up front, before the first search: *all four report sets stated by filename with none of the earlier three re-audited and none of W21c's three corrections redrafted; every explicit novelty/absence claim in the newly collected reports extracted with `file:line` and tested by literal search against **both** the corpus at the corrected root **and** the live tree; W24 read in depth as the priority; the falsifying source named and quoted verbatim with a smallest correct restatement for every contradiction; and the recurrence of the two known propagating defects reported as a separate count.*

**MET.** Four sets stated: 48 / 36 / 22 / 17 (16 audited, 1 HELD). 50 claim lines classified into 16 clusters: **1 CONTRADICTED**, **11 CORROBORATED**, **3 STANDING**, 1 deliberately not re-tested, the rest NOT TESTABLE. One correction drafted verbatim; no report rewritten. **Recurrence count delivered: 0/16 for the junction-source absence defect, 0/16 for the EGA-accession claim, 1/16 for a mis-transcribed correction count.** Returning now.

---

## Tool-call and wall-clock count actually used

**11 tool calls**, all `Bash`. **Wall clock 2 min 53 s measured** (`03:17:25Z` → `03:20:18Z`), plus context reading before the first stamp and drafting after the last call. Well inside the ~40-call / ~40-minute self-observed target.

---

## Next concrete action

**Fix `W21b:145`'s table cell at the same time as appending W21c's three corrections — it is the last remaining source of the EGA defect, and it is one line.** W21c correctly diagnosed that appending corrections downstream does not stop a source; the measurement here shows the dispatch-text fix **worked** (0 recurrences of both original defects across 16 reports), and that the only remaining leak is `W21b:145`'s own arithmetic slip, which `W24:240` faithfully transcribed. Correcting *"six … four in the live tree"* to *"seven … five in the live tree, two corpus-only"* in `W21b`'s cell, plus the appended `W24` correction drafted in R2, closes the defect at both its source and its one propagation. No retrieval, no network, no new analysis — coordinator writes only.

**Second, and I recommend it be the lane's last pass:** the marginal yield of this lane is now clearly falling — 3 contradictions in 36 reports (W21b), 3 in 22 (W21c), 1 in 16 (W21d), and the one that broke was a transcription of a correction rather than an original claim. A fifth pass over the next tranche is defensible only if the tranche is large; otherwise the honest recommendation is to close the corpus-differential lane and hand the residual to whoever owns `W24`'s 65 unread reports, whose absence `W24:282` correctly records as **UNKNOWN**.

**Explicitly not a successor, and I recommend against it:** re-auditing any of the three predecessor sets; treating `W25` as auditable by any route while its hold stands; and treating the junction-source `retrieval.json` as anything more than a provenance record — its accessions are already recovered (**DUPLICATE**), its access-and-identity gate was **not passed**, and reading its ENA libraries as patients is the exact inference it forbids.
