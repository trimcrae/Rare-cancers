<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:20:24Z UTC
     agent id afab32bc41d35d6c4 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-afab32bc41d35d6c4.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

## Worker

**W23b**, corpus-root correction re-evaluation lane, OPUS-CAPACITY-CAMPAIGN-20260908. Read-only; advisory. No integration, publication, merge, retrieval or outreach.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) from my own system context. I did not observe the served model; no environment variable in this container names a model. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start: `Tue Sep  8 03:12:46 UTC 2026`** · **end: `Tue Sep  8 03:15:54 UTC 2026`** (report drafted after the end stamp; no further tool calls).

`git rev-parse HEAD` **start: `98a0833f1ede2cf9cef13790388260567a32e868`** · **end: `41781ee59e0beb852b77d80147cc385b4456b648`**. **The checkout moved under me mid-run.** I did not move it — I performed no git write operation of any kind. `git status --porcelain` **start:** 8 untracked lines, all `research/autonomy/opus-capacity-campaign-20260908/reports/W*.md` (W01g, W02f, W04e, W06f, W07f, W09f, W12e, W20g); **end: empty** — the coordinator committed those eight reports during my run. Every report line:number I cite below was read at one of these two HEADs and I re-state it as a citation into report text, not into a pinned blob.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — literal at end of run; five long proxy host-list variables (`no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `JAVA_TOOL_OPTIONS`, `npm_config_noproxy`) were present in the raw output and are filtered here for length only, remainder sorted:

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

---

## Question

Under the corrected repository-relative corpus root `/tmp/claude-0/frozen-corpus/extracted/corpus/`, which of W23's novelty and absence claims survive, which are superseded, and which become UNKNOWN — and which other collected reports carry a claim built on the wrong root?

It is open because the ~02:58Z `WAVE-LOG.md` correction established the root error and named W23 rank 3 as needing its scope restated, but no worker had re-run W23's claims at the corrected root or put the corrected root's full membership on the record.

---

## Prior-work check

Read in full: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `WAVE-LOG.md` §~02:58Z (and the ~03:05Z W25 section that follows it), `reports/W23-cross-output-synthesis-packet.md`, `reports/W21b-corpus-differential-second-pass.md`, `reports/W25-gse243553-candidate-merit.md`.

I am **not replaying** and did not touch: any Brenca route or origin gate; the NR4A Perspective refusal; PUB-EMC-CLASSIFICATION; the paired-Davis negative; W11c's decline-on-merits; any egress route. **No network call of any kind was made.** No retrieval, no re-upload, no source request. All execution under `/tmp/claude-0/w23b/`. `scripts/preflight.sh` not run.

W21b and W25 already found the root error from two other directions. **This report does not re-derive their findings and does not supersede them**; it extends them to (a) W23's remaining claims, (b) the full corrected-root membership, (c) a systematic sweep of all 121 reports.

Commands (abridged; full set under Validation evidence):

```
grep -rn "frozen-corpus/extracted" reports/ | grep -v "extracted/corpus"
grep -rn "extracted/\(research\|systems\|scripts\|AGENTS\|CLAUDE\|README\)" reports/ WAVE-LOG.md
grep -rn -i "not in the .*frozen corpus\|absent from .*corpus\|corpus contains no" reports/
```

---

## Method / inputs

- **Live checkout** `/home/user/Rare-cancers` @ `98a0833f…` → `41781ee5…` (see Worker). Read-only.
- **Frozen corpus**, corrected root `/tmp/claude-0/frozen-corpus/extracted/corpus/`, read in place, not copied, not overlaid. Whole-ZIP identity already verified by the coordinator and by W23 at sha256 `b474cd2f…`; I did not re-verify the ZIP, I verified the extracted tree.
- **Metadata** `/tmp/claude-0/frozen-corpus/extracted/metadata/{member-manifest.json,tracked-file-map.txt}`.
- Tools: GNU `find`, `stat`, `sha256sum`, `grep`, `awk`, `comm`, `xargs`, `python3` (stdlib `json` only). No third-party packages, no network.

---

## Result

### 1 · The three named files — verified independently (PRIMARY)

My own `stat -c%s` + `sha256sum` at the corrected root, exit 0:

| Corpus path (root `…/extracted/corpus/`) | bytes | sha256 | matches brief? |
|---|---:|---|---|
| `research/autonomy/nr4a3-patient-junction-source-2026-09-07/README.md` | 7227 | `55dc009f52373fa28faf9aa22037db552f9625aee7646f3d3d8957794e1750c2` | **yes** |
| `research/autonomy/nr4a3-patient-junction-source-2026-09-07/retrieval.json` | 3870 | `a5216ca7edcf00694cf58625f85cf991f77d3b85aea1a19902aef998aefee273` | **yes** |
| `research/autonomy/next-paper-2026-09-07/additional-source-provenance/brenca-correction-pubmed.json` | 2599 | `c83fbdbf5adb54721a59088f5db824d099960bc56d05b191019e74ea9a343172` | **yes** |

All three byte counts and all three digests reproduce exactly. **PRIMARY.**

### 2 · Full membership of the corrected root — on the record (PRIMARY)

`find . -type f` at `…/extracted/corpus/`: **5,996 regular files, 0 symlinks, 236,150,544 bytes total** — matching `CORPUS-CONTEXT.md` exactly.

I computed sha256 and byte size for **every one of the 5,996** and compared against the 5,996 `corpus/`-prefixed entries of `metadata/member-manifest.json`:

```
manifest corpus/ entries: 5996
in mine not manifest:     0
sha256 mismatches:        0
size mismatches:          0
```

**Consequence for the record: `metadata/member-manifest.json` IS the authoritative per-file size+sha256 enumeration of the corrected root, and I have now verified byte-for-byte that its `corpus/`-prefixed rows correspond one-to-one to the extracted tree at the corrected root.** Pasting 5,996 lines here would duplicate a file the campaign already holds and would not add evidence; the durable artifact is the manifest plus this verification. My independently computed listing (`<sha256> <bytes> <relpath>`, sorted by path) is at `/tmp/claude-0/w23b/listing.txt`, itself sha256 **`e1b6ce1c1c0d69cedeb1914717a5ce29c8c8acaf66bcd56b3f911e1f45ddf7e2`**, 5,996 lines. That is a scratch file outside the repository; the coordinator may collect it if a standalone listing is wanted in-tree.

Directory-level shape of the corrected root, so its scope is legible without re-derivation (PRIMARY, my `awk` over the listing):

| Top-level group | files | bytes |
|---|---:|---:|
| `research/autonomy/` | 2725 | 111,392,380 |
| `research/modalities/` | 2057 | 87,435,764 |
| `research/manuscripts/` | 540 | 20,873,171 |
| `.github/workflows/` | 173 | 2,208,113 |
| `systems/views/` | 113 | 1,578,094 |
| `research/release-candidates/` | 111 | 1,325,837 |
| `research/literature/` | 89 | 5,238,032 |
| `scripts/` (incl. `scripts/tests/` 24) | 74 | 1,038,857 |
| `research/compute/` | 25 | 472,639 |
| `systems/` (graph 19, tests 16, schema 11, taxonomy 3, + 12 loose) | 61 | 2,591,556 |
| `research/hypotheses/` | 10 | 217,927 |
| `.github/scripts/` | 3 | 4,365 |
| `research/routines/` 2, `research/data/` 2, `research/meta/` 1 | 5 | 140,478 |
| loose `research/*.md|json` (IDEAS, PROTOCOL, README, method-watch ×8, field-scan-log, operating-environment-backfill) | 13 | 1,533,516 |
| root `AGENTS.md`, `CLAUDE.md`, `README.md` | 3 | 13,700 |
| **total** | **5996** | **236,150,544** |

Two structural facts that matter for every future absence check, both measured here:

- `research/autonomy/opus-capacity-campaign-20260908/` is **absent from the corrected root** (`find -path '*opus-capacity*'` → empty). Expected and correct: the snapshot base `93b75888…` predates this campaign. **A report's absence from the corpus is therefore never evidence of anything about that report.**
- `metadata/tracked-file-map.txt` has **10,566 rows** versus 5,996 files present — the gap `CORPUS-CONTEXT.md` already warns about. A map row proves a blob existed at `93b75888…`; it does not make the bytes available here.

### 3 · W23 claim-by-claim under the corrected root

**Claim W23-A — `W23:223`.** Asserted: *"`research/autonomy/nr4a3-patient-junction-source-2026-09-07/` **does not exist at the pinned tip `d3e9c4d8…`**, and it is **not** in the 5,996-file frozen corpus."*

What the corrected root actually holds — `find … -type f | sort`, 13 files:

```
research/autonomy/nr4a3-patient-junction-source-2026-09-07/README.md
…/brenca-origin-gate.csv
…/compare_published_calls.py
…/coordinator-verification.json
…/delite-model-metadata.csv
…/published-call-comparison.json
…/recover.py
…/retrieval.json
…/sources/brenca-article.xml
…/sources/brenca-ena-runs.tsv
…/sources/brenca-project.xml
…/sources/delite-article.xml
…/sources/urbini-article.xml
```

`README.md` verbatim, my `sed -n '1,16p' | cat -n` and `grep -n`:

- L2–L7: `id: DOC-NR4A3-PATIENT-JUNCTION-SOURCE-20260907` / `title: Patient fusion-junction source gate and published-call comparison` / `kind: memo` / `status: live` / `date: 2026-09-07` / `last_verified: 2026-09-07`
- L13–L14: *"The proposed original patient-read study did not pass its access and specimen-identity / gate. No raw reads were downloaded or aligned."*
- L24–L25: *"PRJNA692081 / SRP301712. The preserved ENA report has 23 paired libraries, 46 FASTQs / and 46,317,317,021 compressed bytes. This is an access observation, not 23 patients."*

`retrieval.json` opens (bytes 0–~180): `"retrieved_utc": "2026-09-07T16:03:02.699465+00:00"`, `"free_bytes_before": 38476955648`, **`"raw_reads_downloaded": false`**, then a `files[]` array whose first two members are `sources/brenca-methods.docx` (26,782 B, sha256 `89b3f638…`) and `sources/brenca-table-s1.xlsx`, both from `pmc-oa-opendata.s3.amazonaws.com/PMC6766969.1/`.

**Verdict: first half SURVIVES, second half SUPERSEDED.** Correct restatement: *absent from the live checkout at every HEAD this campaign has read; present in the frozen corpus as 13 files, now read there.* Identical to W21b's N1 finding, reached independently.

**Claim W23-B — `W23:385`.** Same assertion in the conclusions block. **SUPERSEDED**, identically.

**Claim W23-C — `W23:225` / `W23:235`, "missing input: the directory itself, so `retrieval.json` can be read at integration."** **SUPERSEDED.** `retrieval.json` is present at the corrected root and I have read it. It is no longer a missing input; it is an available, unread-by-W23 input. Note precisely what it does and does not settle: it records what was fetched and that **no raw reads were downloaded**. It contains no accession-to-case key, so it does not move the obtainable-band denominator by itself.

**Claim W23-D — `W23:221`, the Rank 5 DUPLICATE classification and its scientific guards** (accessions already recovered → DUPLICATE never novelty; no cohort/independence/patient claim; 15 unresolved libraries ≠ 15 patients; specimen count 12). **SURVIVES, and the corrected root strengthens it.** The directory's own README says the access-and-identity gate was not passed and states verbatim that 23 paired libraries is *"an access observation, not 23 patients."* The correction upgrades W23's Rank 5 from SECONDARY-transcribed to readable-at-the-corrected-root; **it changes nothing about the closure.**

**Claim W23-E — `W23:195`, Rank 3 novelty, part 1: "`grep -rl -i "GSE243553" --exclude-dir=.git .` returns four retained JSON artifacts plus two scripts and a test."** This was run against the **live checkout**, and as a live-checkout statement it is scoped and fine. At the corrected root the same grep returns **39 files**; the live tree at `41781ee5…` returns 63 (inflated by campaign reports). Five corpus files hit GSE243553 that are **absent from the live tree entirely**:

```
research/autonomy/next-paper-2026-09-07/selection.md
research/autonomy/nr4a3-program-source-2026-09-07/retrieve-paper.py
research/autonomy/nr4a3-program-source-2026-09-07/retrieve.py
research/autonomy/nr4a3-program-source-2026-09-07/source-manifest.jsonl
research/autonomy/nr4a3-program-source-2026-09-07/sources/geo.txt
```

**Verdict: SUPERSEDED as a repository-wide statement, SURVIVES as a live-checkout statement.** This is the same false-absence shape W25 diagnosed at `W25:100`.

**Claim W23-F — `W23:195`, Rank 3 novelty, part 2: "no `.bed` is tracked anywhere."** `find … -name '*.bed'` at the corrected root → **zero**. `grep -c '\.bed$'` over `tracked-file-map.txt` → **0**. **SURVIVES**, at the corrected root and against the base-`93b` tracked map. The correct nuance, which W23 did not have: the marker BEDs are tracked *inside* `research/autonomy/nr4a3-program-source-2026-09-07/sources/markers.zip` (788,065 B, blob `9c225b07…`, tracked-file-map L2220), so no `.bed` path is tracked while the BED content is.

**Claim W23-G — `W23:195`, Rank 3 novelty, part 3: "No pairwise comparison between GSE243553 peaksets exists anywhere in the repository." This is the load-bearing sentence of the rank-3 novelty case, and under the corrected root it does not hold as written.**

`/tmp/claude-0/frozen-corpus/extracted/corpus/research/autonomy/nr4a3-program-tissue-2026-09-07/outputs/overlap.tsv` — **76,949 B, sha256 `ee7a53c8abd0f6c0172b2f4261074d001107487742a7757de6db4374750abfcc`, 1,585 lines (header + 1,584 rows)** — is a **complete pairwise Jaccard table over exactly the 32 GSE243553 programs**, at three windows. Header and first rows verbatim:

```
window_bp	program_a	program_b	intersection	union	jaccard
1000	ACTB-GLI1	ACTB-GLI1	2	2	1.0
1000	ACTB-GLI1	ARFGEF2-HNF4A	0	190	0.0
1000	ACTB-GLI1	CCDC6-RET	0	959	0.0
1000	ACTB-GLI1	EPC1-PHF1	0	5	0.0
```

`awk` over column 2 gives **32 distinct programs**: `ACTB-GLI1 ARFGEF2-HNF4A CCDC6-RET EPC1-PHF1 ETV6-NTRK3 EWSR1-ATF1 EWSR1-CREB1 EWSR1-DDIT3 EWSR1-ETV1 EWSR1-ETV4 EWSR1-FEV EWSR1-FLI1 EWSR1-NFATC2 EWSR1-NR4A3 EWSR1-PBX1 EWSR1-POU5F1 EWSR1-SP3 EWSR1-YY1 FGFR3-TACC3 FUS-ATF1 FUS-DDIT3 FUS-FEV HEY1-NCOA2 IRF2BP2-CDX1 MEAF6-PHF1 PAX7-FOXO1 SS18L1-SSX1 TAF15-NR4A3 TCF12-NR4A3 TFG-NR4A3 TMPRSS2-ERG TPR-NTRK1`; column 1 gives windows `1000 2000 5000`. 3 × (32·33/2) = 1,584 rows exactly — a full unordered self-inclusive 32×32 panel at three windows. This is the same 32-member panel and includes all four NR4A3 fusions W23's rank 3 is about.

Provenance to GSE243553 is chained and checkable: `…/nr4a3-program-source-2026-09-07/outputs/bed-members.tsv` (4,298 B, 33 lines = header + 32) is the per-member inventory of `Supp_Data_1_new/*_markers.bed` with `program / zip_member / bytes / sha256 / raw_peaks / unique_peaks / duplicate_peaks`; its rows reproduce **W20b's own recorded sizes exactly** — `EWSR1-NFATC2 … 17345 … 724 peaks` and `TPR-NTRK1 … 3899 … 161 peaks`. `…/nr4a3-program-source-2026-09-07/sources/geo.txt` opens `^SERIES = GSE243553`, `!Series_pubmed_id = 39048711`, Frenkel/PROD-ATAC.

**What `overlap.tsv` is, stated precisely so the correction is not overstated.** `nr4a3-program-tissue-2026-09-07/analyze.py:192` computes it over **gene-symbol program membership**, not over peak intervals:

```
a=set(members[w][p]); b=set(members[w][q]); overlaps.append(dict(window_bp=w,program_a=p,program_b=q,intersection=len(a&b),union=len(a|b),jaccard=len(a&b)/len(a|b)))
```

with `members` built at `:76`/`:126` from rows keyed `symbol` / `program` / `window_bp`, i.e. genes whose TSS falls within `window_bp` of a program's peaks. `protocol-20260907.md:73` states the intent: *"publish overlap counts, Jaccard values, and each gene's effective F/B/D weight."* So it is a **promoter-window gene-set Jaccard**, not the genomic-interval Jaccard W19c/W20b ran.

**Verdict: SUPERSEDED as written; a narrower claim SURVIVES.** *"No pairwise comparison between GSE243553 peaksets exists anywhere in the repository"* is false at the corrected root — a full 32×32×3-window pairwise Jaccard over the same 32 GSE243553 programs was already computed and retained. What survives is the narrower, and now necessary, formulation: *no pairwise **genomic-interval** Jaccard between the GSE243553 peaksets exists in the corrected root or the live tree; the retained pairwise comparison is over promoter-window gene-set membership.* Whether that residue clears a novelty bar is the scientific owner's call, not mine — and **W25 has independently already recommended declining rank 3 on novelty, for different reasons (prior art in `next-paper-2026-09-07/selection.md` L56–58 and `nr4a3-program-source-2026-09-07/README.md` L53). My finding is a second, independent hit on the same claim, from the comparison side rather than the prior-art side.**

**Claim W23-H — `W23:201`, "Exact candidate-specific missing input: GSE243553 `MOESM3_ESM.zip`, `Supp_Data_1_new/*_markers.bed` … behind a 403 CONNECT policy denial from this container."** **PARTLY SUPERSEDED; the 403 itself SURVIVES untouched.** The 403 from this container is real, I did not test it and did not route around it. But the framing "missing input" is wrong at the repository level: `sources/markers.zip` (788,065 B) and `outputs/peaks.tsv` (3,041,469 B) are **tracked at base `93b75888…`** (tracked-file-map L2200, L2220), and `outputs/bed-members.tsv` — with per-member size, sha256 and peak counts for all 32 — is **present in the corrected root and readable now**. The interval *bytes* are absent from `corpus/` and absent from the live checkout: that is a **snapshot-selection and branch-lineage gap, not an access gap**. This reproduces W25:178 independently. The bytes themselves remain **UNKNOWN as to availability in this container**, per `CORPUS-CONTEXT.md`.

**Claim W23-I — `W23:197`, the Rank 3 statistical caveats** (chr1 prefixes only; 36 shared intervals; ARM 2 n=4, three of four EWSR1↔FUS swaps; ASSOCIATION never mechanism; no clinical claim). **SURVIVES entirely.** Nothing at the corrected root touches these, and the honest-bar statement at `W23:199` (*"a real result but a thin paper … does not yet clear a submission bar"*) survives and is if anything reinforced.

**Claim W23-J — `W23:211`, Rank 4: "the retained Windows failure logs **do not exist in the tree**."** **SUPERSEDED as a repository-wide statement; SURVIVES as a live-checkout statement.** At the corrected root: `research/autonomy/peerj-validation-audit-2026-09-07/validation/{windows-platform-outcome.json, full-windows-manuscripts-partial.txt, full-windows-owned-processes.json, full-windows-platform-stop.json}` are all present. W21:171 found this first and drafted the narrowing; I confirm it at the corrected root. W23 was relaying W12's own honest self-correction, so **the fault is inherited, not W23's**, and W12's measured Linux findings are untouched.

**Claim W23-K — `W23:386`, "The frozen corpus is a selected-file snapshot, not a `93b` checkout. Absence from it is UNKNOWN, never proof of absence and never source novelty."** **SURVIVES, and is exactly right.** W23 stated the correct epistemic rule and then, at `:223`/`:385`, made a factual error about membership rather than an error of rule. The corrected root vindicates the rule: 10,566 map rows vs 5,996 present files.

**Claim W23-L — `W23:119–135`, the corpus re-verification block** (ZIP 45,840,377 B, sha256 `b474cd2f…`, 6,002 members, `testzip()` → `None`, 0 unsafe, 0 symlinks; and the explicit refusal to claim the 6,001-file pass as its own). **SURVIVES.** I verified the extracted tree rather than the ZIP and found 5,996 files / 236,150,544 bytes / 0 symlinks, consistent throughout. W23's method here was sound; the root error was in its *searches*, not its verification.

**Claims W23-M — the remaining ranks** (Rank 1 W11b, Rank 2 fake-guard, Rank 6 inventory). **Unaffected by the root correction**, with one exception already noted: `W23:235`'s missing-input line for Rank 6 is superseded in the same way as W23-C. Rank 6's substantive verdict (*"Do not manufacture a paper from it"*, `W23:233`) **SURVIVES** — but its stated reason *"a directory nobody in this campaign can read"* is now false, so the coordinator should keep the verdict and replace the reason with the real one: the band moved 32–51 → 44–63 on one correction and `CLOSED-WORK.md` forbids inventing independent cohorts.

### 4 · Sweep of the other reports for wrong-root claims

**A methodological correction the coordinator needs, because it changes what has to be re-checked.** The root error only bites when a path is **joined** (`extracted/` + `research/…`), not when a tool **recurses** from the outer root — `rg` and `find` both descend into `corpus/`. `grep -rn "extracted/\(research\|systems\|scripts\|AGENTS\|CLAUDE\|README\)"` across all reports and `WAVE-LOG.md` returned **zero hits**. So `W08f:96` (`rg -l … /tmp/claude-0/frozen-corpus/extracted`), `W20e:89` (`find /tmp/claude-0/frozen-corpus/extracted -iname "*.fa" …`) and `W14c:90` (`rg -n "_probe_tsv_body" /tmp/claude-0/frozen-corpus/extracted/`) are **recursive and therefore correct**; they need no correction. The ~15 further reports that merely name the outer directory when describing what they read (W03d:74, W05e:110, W07d:17, W09d:16, W09e:17, W10e:31, W11d:119, W12c:73, W12d:69, W12e:76, W15e:65/105, W15f:91, W17g:27, W21:110, W21b:114, W25:114) are **descriptive, not defective** — several explicitly say they read `corpus/` beneath it.

**Claims that actually need routing** — false or over-broad corpus-absence, with file:line:

| # | Location | Claim as written | Status under the corrected root |
|---|---|---|---|
| 1 | `reports/W23-cross-output-synthesis-packet.md:223` | junction-source dir *"is **not** in the 5,996-file frozen corpus"* | **FALSE** — 13 files present. Already drafted by W21b:186 |
| 2 | `reports/W23-cross-output-synthesis-packet.md:385` | same, in conclusions | **FALSE** — same correction needed, second location |
| 3 | `reports/W23-cross-output-synthesis-packet.md:225`, `:235` | `retrieval.json` is a *"missing input"* | **FALSE** — present and read |
| 4 | `reports/W23-cross-output-synthesis-packet.md:195` | *"No pairwise comparison between GSE243553 peaksets exists anywhere in the repository"* | **FALSE as written** — `nr4a3-program-tissue-2026-09-07/outputs/overlap.tsv`, 1,584 rows, 32 programs × 3 windows. **Not previously routed by anyone; this is the new one** |
| 5 | `reports/W23-cross-output-synthesis-packet.md:195` | live-tree GSE243553 grep presented inside a repository-wide novelty verdict | **OVER-BROAD** — 5 corpus-only files; scope to "live checkout" |
| 6 | `reports/W23-cross-output-synthesis-packet.md:211` | *"retained Windows failure logs do not exist in the tree"* | **OVER-BROAD** — 4 files present in corpus. W21:171 already drafted the narrowing |
| 7 | `reports/W01f-obtainable-band-stability.md:89` | junction-source dir *"is absent from this checkout **and from the frozen corpus**"* | **FALSE (second half)** — same error as W23:223. **Not previously routed; W21b's table covers W23 and W01e but not W01f** |
| 8 | `reports/W23-cross-output-synthesis-packet.md:201` | marker BEDs are a missing input behind a 403 | **PARTLY FALSE** — tracked at `93b`; `bed-members.tsv` present. Already routed by W25:178. The 403 itself stands |

**Claims I checked that are correct and need no action** — stated as plainly as the failures:

- `W01e:82`, `W01g:90` — scoped to "this HEAD" / "this checkout". **SURVIVE**, exactly as W21b:146 already judged W01e.
- `W24:210` — already states *"Absent from the live checkout …; PRESENT in the frozen corpus as 13 corpus-only files."* **CORRECT**, no action.
- `W25:100`, `:128`, `:178`, `:253`, `:275`, `:276` — all correctly rooted and correctly hedged. **SURVIVE.**
- `W21b:125`, `:138`, `:144`, `:146`, `:186`, `:206`, `:294` — the correction itself. **SURVIVES**, independently reproduced here.
- `W08e:285` — *"W08d's report … is absent from the tree at HEAD `47aac85` and from the frozen corpus."* **SURVIVES.** I verified the campaign directory is genuinely absent from the corrected root (snapshot base predates the campaign). The inference drawn from it — SECONDARY (TRANSFERRED), load-bearing, honestly flagged — is correct. It would nonetheless read better scoped, since corpus absence of a campaign report is structural, not informative.
- `W15e:332` — *"`denominator_unit` is absent from the selected frozen corpus … absence is UNKNOWN, not proof."* **SURVIVES.** `grep -rl "denominator_unit"` at the corrected root → **0 files**. Correct fact, correctly hedged. W21b:206 was right that W15e is the one report that pre-emptively tested itself against the corpus.
- `W20e:89`, `:123` and `W20f:361` — no FASTA in corpus. **SURVIVE** (recursive `find` from the outer root; correct).
- `W21:130`, `:171` — corpus differential. **SURVIVE.**
- `W02e:107` — *"no exact per-gene / per-sample variance decomposition … exists in the tree or in the frozen corpus."* **UNKNOWN.** The report does not state which root it searched and the claim is not a simple path test; I did not verify it and I am not asserting it is wrong. Flagged for the coordinator only as unverified, not as defective.

**Not a corpus claim, so out of scope here but noted because the sweep surfaced it:** `W10:64` ("PMID absent from corpus", 19 / 22.6%) and `W09b:167,373,638` use "corpus" to mean the *literature* corpus, not the frozen file corpus. No correction implied.

---

## Validation evidence

All `RUN`. Environment: `/home/user/Rare-cancers` (read) and `/tmp/claude-0/w23b/` (execute); GNU coreutils/grep/awk, `python3` stdlib only; **no network**.

**RUN 1 — the three named files.** `stat -c%s` + `sha256sum` at the corrected root, all `PRESENT`, exit 0. Output in Result §1; all six values match the brief.

**RUN 2 — membership.** `find . -type f | wc -l` → `5996`; `find . -type l | wc -l` → `0`; `xargs … sha256sum | wc -l` → `5996`; `awk '{s+=$1}'` over `stat -c '%s %n'` → `total bytes: 236150544`. Exit 0.

**RUN 3 — manifest cross-check.** `python3` (stdlib `json`) against `metadata/member-manifest.json` (`members` = 6,001 entries; 5,996 with `corpus/` prefix):
```
manifest corpus/ entries: 5996
in mine not manifest: 0 []
sha256 mismatches: 0
size mismatches: 0
```
Exit 0. Listing `/tmp/claude-0/w23b/listing.txt`, 5,996 lines, sha256 `e1b6ce1c1c0d69cedeb1914717a5ce29c8c8acaf66bcd56b3f911e1f45ddf7e2`.

**RUN 4 — junction-source directory.** `find … -type f | sort` → 13 paths (listed in Result §3). `sed -n '1,16p' README.md | cat -n` and `grep -n` → L2–L7, L13–L14, L24–L25 quoted verbatim above. `head -c 700 retrieval.json` → `"raw_reads_downloaded": false` and the first two `files[]` members. Exit 0.

**RUN 5 — GSE243553 differential.** `grep -rl -i "GSE243553"`: live tree 63 files, corrected root 39 files; `comm -13` (live minus campaign reports, vs corpus) → the 5 corpus-only paths listed. Exit 0.

**RUN 6 — the pairwise table.** `wc -l overlap.tsv` → `1585`; `stat -c%s` → `76949`; `sha256sum` → `ee7a53c8…`; `awk` distinct `program_a` → `32`, distinct `window_bp` → `1000 2000 5000`; `head -5` quoted verbatim. `grep -n` on `analyze.py` → line 192 (the Jaccard construction, quoted verbatim) and lines 76/126 (`members` construction). `grep -n` on `protocol-20260907.md` → line 73. Exit 0.

**RUN 7 — BED provenance.** `head -3 bed-members.tsv` + `wc -l` → header + 32 rows; `grep -E "EWSR1-NFATC2|TPR-NTRK1"` → `17345 … 724` and `3899 … 161`, matching W20b. `head -12 sources/geo.txt` → `^SERIES = GSE243553`, `!Series_pubmed_id = 39048711`. Exit 0.

**RUN 8 — interval bytes and tracked map.** `find` for `peaks.tsv|peak-gene-links.tsv|markers.zip|program-membership.tsv|tss.tsv` at the corrected root → **empty**. `grep -n` on `tracked-file-map.txt` → L2199–L2203, L2220 with sizes 4,579,392 / 3,041,469 / 2,709,678 / 11,042,624 / 788,065. `grep -c '\.bed$'` on the map → `0`; `wc -l` map → `10566`. Exit 0/1 as appropriate.

**RUN 9 — report sweep.** The three `grep -rn` commands under Prior-work check, plus `grep -rn -i "not in the .*frozen corpus\|absent from .*corpus\|corpus contains no"`. The path-join grep returned **no output** (exit 1). Outputs are the basis of §4 and every file:line there was read in the grep output.

**RUN 10 — structural checks.** `find $C -path '*opus-capacity*'` → empty. `find $C -path '*peerj-validation-audit-2026-09-07*' -name 'windows*' …` → 4 paths. `grep -rl "denominator_unit" $C | wc -l` → `0`. Exit 0.

**PROPOSED (NOT RUN):** nothing. I ran everything I report.

---

## Limitations

- **I did not verify the ZIP.** I verified the extracted tree at the corrected root and its agreement with `member-manifest.json`. W23 and the coordinator hold the ZIP-level evidence; I did not duplicate it.
- **The corpus is a selected snapshot.** 10,566 tracked-map rows vs 5,996 present files. Absence from the corrected root is still **UNKNOWN**, never proof of repository-wide absence, never source novelty. That rule survives this correction entirely — the correction is about a *false absence*, and it makes the rule more important, not less.
- **A correction supersedes, it does not erase.** W23, W01b, W01e and W01f stated honestly that they had not read these files. That honesty is preserved. Their reports stand as accurate records of what was reachable from the live checkout.
- **`overlap.tsv` is a gene-set Jaccard, not an interval Jaccard.** I have not claimed it duplicates W19c/W20b's analysis. It falsifies W23's sentence as written; it does not by itself settle whether an interval-level analysis is novel. That judgement is the scientific owner's.
- **I did not read the primary publication.** `nr4a3-program-source-2026-09-07/sources/paper.html` (301,282 B, PMC13105821) is tracked at `93b75888…` and absent from both the corrected root and the live checkout, exactly as W25:275 records. My novelty statements about rank 3 rest on repository artifacts, not on the paper's text.
- **No clinical claim of any kind follows from anything here.** There is no wet lab. Nothing in this report is a cohort, independence, patient, efficacy, safety or selectivity claim. The Brenca closure is untouched: the accessions remain **already recovered and DUPLICATE, never novelty**; 23 libraries are not 23 patients; the paper-stated specimen count is 12.
- **The checkout moved mid-run** (`98a0833f…` → `41781ee5…`). Report line numbers are stable across that move for the eight files that changed status (untracked → committed, content unchanged), but a future reader should re-resolve line numbers against a stated HEAD.
- **I am read-only.** I wrote nothing under `/home/user/Rare-cancers` or under `/tmp/claude-0/frozen-corpus/`. Every correction above is a routing recommendation for the coordinator, not an edit.

---

## Stop condition

**Set at start:** return as soon as (a) the three named files are independently verified at the corrected root, (b) every novelty/absence claim in W23 is classed SURVIVES / SUPERSEDED / UNKNOWN with verbatim corrected-root evidence, (c) the corrected root's full membership is enumerated and cross-verified so it need not be re-derived, and (d) the other reports are swept for wrong-root claims with file:line. **MET** — all four. I stopped on meeting it and did not extend into adjacent lanes.

---

## Tool-call and wall-clock count actually used

**32 tool calls** (all `Bash`; no writes to the repository or the corpus, no network, no git write operation, `scripts/preflight.sh` not run). **Wall clock ≈ 5 minutes** of tool execution, `03:12:46Z` → `03:15:54Z`, plus drafting. Both well inside the ~40/~40 target.

---

## Next concrete action

**One coordinator write, no retrieval and no new analysis: append a single dated correction block to `WAVE-LOG.md` carrying the eight routed items in §4 above, with `reports/W23-cross-output-synthesis-packet.md:195` and `reports/W01f-obtainable-band-stability.md:89` flagged as the two not yet covered by W21b or W25.** The W23:195 item is the one with scientific consequence: the sentence *"No pairwise comparison between GSE243553 peaksets exists anywhere in the repository"* must be narrowed to *"no pairwise **genomic-interval** Jaccard … ; a promoter-window gene-set Jaccard over the same 32 programs is retained at `research/autonomy/nr4a3-program-tissue-2026-09-07/outputs/overlap.tsv` (76,949 B, sha256 `ee7a53c8…`, 1,584 rows)"* — and that narrowing is a **second independent reason** alongside W25's prior-art subtraction for the owner to weigh before rank 3 is treated as the campaign's strongest paper opportunity. The decision is the owner's; this is evidence for it, not a decision.
