> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).
> Coordinator note: the owner's later terminal execution of the W11b pair (18 passed, exit 0;
> negative control 7 failed/11 passed, exit 1) supersedes this packet's standalone-verification
> line, which correctly recorded W11b's own claim rather than an observed run.

---

Stop condition met. Packet below.

---

## Worker

**W23**, cross-output synthesis and adjudication packet, OPUS-CAPACITY-CAMPAIGN-20260908. Advisory only — no integration, publication, merge or outreach authority; the scientific owner retains all of it.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) from my own system context. I did not observe the served model, and no environment variable in this container names a model. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start: `Tue Sep  8 02:37:06 UTC 2026`** · `date -u` **end: `Tue Sep  8 02:40:00 UTC 2026`**

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — literal at end of run; five long proxy host-list variables (`no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `JAVA_TOOL_OPTIONS`, `npm_config_noproxy`) present in the raw output and filtered here only for length, sorted:

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

**Write isolation honoured.** Zero files created or modified under `/home/user/Rare-cancers`; `git status --porcelain | wc -l` → `0`. All execution under `/tmp/claude-0/w23/`. No git write operation. One `git fetch` (read-only) was performed to pin the output branch.

---

## Question

Against the supplied global closure map (`CLOSED-WORK.md`) plus the 4878 supplemental terminal dispositions, **which of this campaign's incoming code/source assets, and which single paper opportunity, actually clear the bar — and what is the correct integration disposition for the W11b source-index repair given the writer-vs-cloud tier-base divergence?**

Open because 70 collected worker reports have never been compared against each other, and because the W11b integration question turns on a measurement (the writer-base tier count) that no report in this campaign holds.

---

## Prior-work check

I am a synthesis lane; my prior-work obligation is to confirm each ranked item against the closure map rather than to claim discovery. Commands run and what they showed:

- `ls research/autonomy/opus-capacity-campaign-20260908/reports/ | wc -l` → **70** reports at the pinned tip.
- `awk '/^### /{name=$2} /^result: /{...}'` over all 70 → one-line result extracted per report; used as the ranking frame.
- Per-report execution-evidence census: `for f in *.md; do grep -c -E 'EXIT=|exit=0|exit code|Exit: |EXIT_CODE' "$f"; grep -c -i 'PROPOSED (NOT RUN)' "$f"; done` → full table reproduced in §Validation. **Ten reports carry zero exit-code markers** (W01b, W01d, W02, W02b, W04, W07, W07b, W10, W10b, W10d, W12).
- `cat` of `CLOSED-WORK.md` in full, plus `WAVE-LOG.md` including its **02:40Z dated Brenca correction** (lines 414–457).
- `git show ad34f06b:research/autonomy/cloud-inputs-2026-09-08/input-status.json` and the extracted `terminal-integration.json` — the six 4878 terminal dispositions.
- `grep -n "commit-loop" -A 12 scripts/tier-budgets.json`, `grep -n "def count_dir" -A 14 scripts/tier_budget.py`.

**Closed items I confirm I am not replaying:** the restricted NR4A Perspective (not recreated under any label); PUB-EMC-CLASSIFICATION (user-rejected, stays closed); every unrecovered source in `CLOSED-WORK.md` (Pazopanib, anthracycline, sunitinib 2014, trabectedin/RT 2018, Wagner 2020, CTARC 2022) — no route opened, no route replayed; the failed Davis/Hofvander/promoter-transfer/inverse-bounds gates; the closed clinical checkpoints. I opened **no** network route beyond one `git fetch` of the already-named branch. **I am not a second source-index repair owner** — W11b is sole owner and I authored no code for it, only extracted and hashed its delivered bodies.

---

## Method / inputs

**Pinned output branch tip — my own readback:**

```
$ cd /home/user/Rare-cancers && git rev-parse HEAD
d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4
$ git fetch origin claude/confident-bardeen-ji76cd
From https://github.com/trimcrae/Rare-cancers
 * branch              claude/confident-bardeen-ji76cd -> FETCH_HEAD
$ git rev-parse FETCH_HEAD
d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4
$ git log --oneline -3 FETCH_HEAD
d3e9c4d8 Campaign: dated Brenca correction to the wave log, fifth batch of worker reports
7d081218 Campaign: fourth batch of worker reports (61 collected)
47aac85f Campaign: verified frozen corpus context, wave log, third batch of worker reports
```

**PINNED TIP: `d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4`.** This is two commits ahead of `47aac85f…` (which the owner has read) and later than `b9a0257e…` (the owner's last known tip). The local checkout HEAD equals the remote tip, so my reads are of the pinned tip exactly. `git status --porcelain` → empty.

**Frozen corpus re-verification — my own command output, not the coordinator's numbers:**

```
$ cd /tmp/claude-0/frozen-corpus && stat -c '%s %n' corpus-snapshot.zip
45840377 corpus-snapshot.zip
$ sha256sum corpus-snapshot.zip
b474cd2f8a0e3fa3a253f5b3135379cb26c15222a94698fc411fd781f6346808  corpus-snapshot.zip
sha_exit=0
$ python3 -c "import zipfile; z=zipfile.ZipFile('corpus-snapshot.zip'); ..."
members: 6002
testzip: None
unsafe: 0
symlinks: 0
py_exit=0
```

Whole-ZIP sha256, byte count (45,840,377), member count (6,002), CRC-clean (`testzip()` → `None`), 0 unsafe paths and 0 symlinks all **independently re-verified**. I did **not** re-run the 6,001 per-file sha256 pass — that remains the coordinator's recorded evidence, not mine. `metadata/snapshot-provenance.json` read in full: `"identity": "SNAPSHOT OF SELECTED FILES"`, `is_complete_repository: false`, `contains_git_history: false`, `snapshot_base_commit: 93b75888…`, `no_new_source_material: true`, `no_scientific_acceptance: true`.

**evidence-4878 capsule — extracted from the supporting branch blob and re-verified:**

```
$ git cat-file blob 2a069996273bdf7c53c6313340a86cc1495a5042 > /tmp/claude-0/w23/evidence-4878-exact-files.zip
$ stat -c '%s %n' evidence-4878-exact-files.zip
1137077 evidence-4878-exact-files.zip
$ sha256sum evidence-4878-exact-files.zip
32a802baa78c49bad8a0b6555d282230b618f9c97ebd046a98f9be23dd5aaa2f  evidence-4878-exact-files.zip
members: 48   testzip: None
```

Both stated figures match. `terminal-integration.json` (9,287 B) read in full — six terminal runs, three `abandoned`, three `integrated`.

---

## Result — the ranked packet

Six items. Three classes are kept strictly separate and are stated per item.

### Rank 1 — W11b source-reuse index repair pair · **DEMONSTRATED (standalone)** / integration **BLOCKED — named missing input**

**Named output files, hashes, anchors.** Both bodies extracted by me from the report and hashed independently:

| File (intended repository path) | Lines | sha256 (my extraction) | sha256 stated by W11b | Match |
|---|---|---|---|---|
| `scripts/source_reuse_index.py` | 1056 | `b3288598378fd55d26d46ed2e4b6575c2357a57abf71b8fcec7bf28edb8337e3` | `b3288598378fd55d26d46ed2e4b6575c2357a57abf71b8fcec7bf28edb8337e3` | **YES** |
| `scripts/tests/test_source_reuse_index.py` | 477 | `49208917bba102cd1bceb4ac932046dcab20609f046303f5dc8476954904136a` | `49208917bba102cd1bceb4ac932046dcab20609f046303f5dc8476954904136a` | **YES** |

Full disposition in §"The W11b disposition" below.

**Importance:** high for repository hygiene, **zero** scientific importance — it is an informational read-only lookup helper and establishes nothing about EMC. **Novelty:** the repair is genuinely new work (nine static findings adjudicated by execution; one, F4, refuted on its own example). **Achievable validation:** already achieved standalone; writer-side validation blocked. **Utility:** contingent on integration.

**Next executable scientific action:** none — this is not a scientific item. **Exact missing input:** the freshly measured writer-base `python3 scripts/tier_budget.py` commit-loop count at the exact current writer inputs (see below).

---

### Rank 2 — W14 + W14b: the fake-guard population and its smallest correct repair · **DEMONSTRATED**

**Anchors.** `research/autonomy/opus-capacity-campaign-20260908/reports/W14-computation-bottleneck.md:112-114` (three generators, `--check` → exit `0` **after writing** the artifact); `:136` (`python3 research/manuscripts/emc_relative_survival.py --check >/dev/null 2>&1; echo $?` → `0`); `:156` `PYTEST_EXIT=1`, `:160` `AssertionError: emc_mortality_decomposition.py --check REWROTE emc-mortality-decomposition.json`; `:167-170` `PATCH_EXIT=0`; `:178` `PYTEST_EXIT=0`; `:183-188` post-repair `--check` on drifted artifacts → `exit=1` for all three. `W14b-guard-coverage-sweep.md:103` (179 confirmed generators), `:116` (of 65 FAKE-GUARD rows, **exactly 1** advertises a check), `:150` (`emc_fourth_cohort_quant.py` overwrites two committed TSVs then hashes what it just wrote; **wired into an enforcement surface**), `:297` `EXIT=0`, `:317` `CONFIRMED GENERATORS: 179`, `:502` (7 of 18 gate rows write only under `--write` — a stated method limit), `:511` (512/512 probed, 45 rows honestly UNDETERMINED).

**Named repository files at risk:** `research/manuscripts/emc_relative_survival.py`, `emc_terminal_events.py`, `emc_mortality_decomposition.py` (W14, repaired in W14's scratch tree, **not** in the repository), and `emc_fourth_cohort_quant.py` (W14b's single highest-severity row, **unrepaired**).

**Assessment.** *Importance:* the highest of any item here for the integrity of everything else — a `--check` that writes what it verifies makes every downstream reproducibility claim unfalsifiable, and W14b shows one such guard is actually wired into a workflow. *Novelty:* not scientific novelty; it is a real defect diagnosis, which `COMMON-BRIEF.md` §5 names as a useful artifact. *Achievable validation:* fully achievable today, offline, no access dependency — W14 already demonstrated the repair passes and the negative control fails. *Utility:* very high and immediate.

**Class caution:** W14's repair was executed **in `/tmp`, not in the tree**. Placing it is a repository change under the owner's authority, and the normal `scripts/preflight.sh` gate has **not** been run with it in place. That step is `PROPOSED (NOT RUN)`.

**Next executable scientific action:** repair `emc_fourth_cohort_quant.py` so its two `.tsv` comparisons read the committed bytes *before* regenerating (the JSON path is already sound), then run the normal `scripts/preflight.sh` on a settled tree. This is the one item on this list where the next action needs no missing input at all.

---

### Rank 3 — GSE243553 partner-side determination of fusion binding location (W20b → W19c) · **DEMONSTRATED analysis; paper = DESIGN PROSPECT, `NOT RUN` as a paper**

This is **the strongest genuinely distinct paper opportunity in the campaign**, and it is the only candidate I judge to clear the bar.

**Anchors.** `W19c-panel-wide-fusion-clustering.md` §3 (ARM 1, full panel, 32 peaksets / 376 non-degenerate pairs): SHARES-3 n=10, mean J 0.1715, **mean residual +0.1513, permutation p = 0.00008, verdict `PREDICTS LOCATION`**; SHARES-5 n=66, residual +0.0094, **p = 0.09782, `does NOT predict location`**; SHARES-NEITHER n=300 reference. §4 (ARM 2, leave-NR4A3-out, 28 peaksets / 277 pairs): SHARES-3 n=4, residual +0.1105, **p = 0.01486**, leave-one-pair-out means 0.1506 / 0.1111 / 0.1395 / 0.1173. §5 negative control (A–M vs N–Z name bucket): **p = 0.10300, `does NOT predict location`** — the control behaved as a control. §1: W20b reproduced **digit-for-digit** under its stated convention (null mean J 0.0160, unconditional p 0.0013, density-matched p **0.0010** across 5,102 density-matched subsets). `W20b-partner-chromatin-interchange.md:189,191` (`SURVIVES density matching`; `LOCATIONALLY COHERENT`), `:161` (Analysis A `NOT COARSELY COHERENT`, p = 0.1419 — explicitly **not** support), `:285-300` verbatim script-emitted verdicts.

**Named data inputs (all committed):** `gse243553-eno3-overlap-supplement.json` (retained chr1 coordinate prefixes), `gse243553-eno3-overlap.json` (`median_width = 500` for all 32 peaksets), `gse243553_eno3_overlap.py`, `peak_rss.py`. Deposit **GSE243553**, primary publication `doi:10.1038/s41587-024-02347-4`, assembly hg38 established from the deposit's own `!Sample_data_processing` line. The intervals are **the authors' own marker calls**; this repository called no peak.

**Novelty check, from W20b's own prior-work commands** (`:97`, `:105`): `grep -rl -i "GSE243553" --exclude-dir=.git .` returns four retained JSON artifacts plus two scripts and a test; **no `.bed` is tracked anywhere**; every `jaccard` hit in the tree is unrelated (`proposal_dedup.py` text shingles; two gene-set Jaccards in the ATR/PPARγ ledger). **No pairwise comparison between GSE243553 peaksets exists anywhere in the repository.** Against the 4878 dispositions this collides with nothing: no terminal run touches GSE243553, and the 47-file capsule contains **no peak coordinates and no GSE243553 material** (`W20b:93`).

**Assessment.** *Scientific importance:* substantial and mechanistically pointed — it bears directly on whether `EWSR1::NR4A3`, `TAF15::NR4A3`, `TCF12::NR4A3` and `TFG::NR4A3` are interchangeable, which the repository and clinical practice both currently assume, and against which Brenca 2019's single-locus SEMA3C ChAP-qPCR already points the other way. *Novelty:* genuinely distinct — not in the tree, not in the closure map, not in the 4878 dispositions, and it generalises W20b rather than repeating it. *Achievable validation:* the current result is exact within its window but rests on **chr1 prefixes only**, on 36 shared intervals in total, and ARM 2 rests on **n = 4 pairs, three of which are EWSR1↔FUS swaps** — W19c states this as a caveat, not a bonus. *Utility:* high, and it is an **ASSOCIATION**, never a mechanism; no clinical claim of any kind follows.

**Honest bar statement.** A paper on the *current* substrate would be a chr1-prefix analysis of someone else's marker calls with an n=4 confirmatory arm. That is a real result but a thin paper. It clears the "genuinely distinct opportunity" bar; it does **not** yet clear a submission bar.

**Exact candidate-specific missing input:** GSE243553 supplementary **`MOESM3_ESM.zip`**, members **`Supp_Data_1_new/*_markers.bed`** — the genome-wide interval sets for all 32 peaksets (W20b records the member sizes, e.g. `EWSR1-NFATC2_markers.bed` 17,345 B, `TPR-NTRK1_markers.bed` 3,899 B). These sit behind a **403 CONNECT policy denial from this container**, which W20b did not test, retry or route around, and neither did I. W19d correctly rules out any successor that needs them from here.

**Next executable scientific action — available today with no missing input:** W19d's named successor. Fix a DNA-binding-domain family assignment for all 32 3′ partners from an external citable source **before** looking at any Jaccard, then re-run the identical machinery with "same 3′ DBD family" as a pre-declared pair class across the full 376-pair panel under both nulls. That converts W19c's post-hoc §3 observation into a prespecified test with a real floor (ETS alone contributes `ETV1 ETV4 FEV FLI1` across two 5′ genes), and it asks whether the 3′ effect is identity-driven or family-driven — a sharper question than 5′-vs-3′.

---

### Rank 4 — W12b locale/encoding rederivation proof · **DEMONSTRATED, partial**

**Anchors.** `W12b-locale-rederivation-proof.md` result line: across **35** `research/manuscripts` generators and **215** real runs, W12's encoding patch **fixes 11**, of which **10 are proven byte-identical to the committed sha256** — named examples `endpoint-regime-map.json` `f542b99d…` and `fusion-junction-aso-submission-tables.md` `cd7f516c…`. 11 exit-code markers in the report; 4 `PROPOSED (NOT RUN)` items.

**Assessment.** *Importance:* moderate — portability hygiene, no scientific content. *Novelty:* W12's own premise was corrected honestly (the retained Windows failure logs **do not exist in the tree**; only a 2026-09-04 prose summary and post-repair PASS logs), so what remains is a real unguarded defect rather than the one W12 was dispatched to find. *Achievable validation:* achieved for the 11; the remainder is explicitly not fixed. *Utility:* moderate; strictly weaker than Rank 2, which it does not overlap.

**Next executable scientific action:** none scientific. **Missing input:** none — the residual is a scoping decision (which of the 35 generators the owner wants patched), not a missing measurement.

---

### Rank 5 — Brenca `PRJNA692081` / `SRP301712` · **DUPLICATE REDISCOVERY** (the standing example)

**Classification is fixed and is not mine to revisit.** Per the owner's correction and the 02:40Z dated `WAVE-LOG.md` entry (lines 414–457): these accessions are **already recovered** in `research/autonomy/nr4a3-patient-junction-source-2026-09-07/` (correction DOI `10.1002/path.5737`; `sources/brenca-ena-runs.tsv` = 23 paired libraries / 46 FASTQ links; `brenca-origin-gate.csv` + `recover.py` = 8 engineered E-N/T-N aliases, **15 unresolved biological origins**; `brenca-correction-pubmed.json` links PMID 34216030 / PMC8451045 to PMID 31020999).

**Therefore:** any recovery of these identifiers or routes is **DUPLICATE, never novelty, never discovery**. **No cohort, independence or patient claim may be built on them** — there is no accession-to-case key. **15 unresolved libraries are not 15 patients, and libraries are not specimens.** The paper-stated specimen count is **12**. W01b's 14-route negative is **preserved** as an accurate record of what was reachable from this cloud checkout; what was wrong was the earlier wave-log inference that nothing was retained anywhere. W01e has already corrected its row to `DEPOSITED — accession known and public` and moved its obtainable band from 32–51 to **44–63**.

⚠ **Verification gap, restated rather than smoothed over.** `research/autonomy/nr4a3-patient-junction-source-2026-09-07/` **does not exist at the pinned tip `d3e9c4d8…`**, and it is **not** in the 5,996-file frozen corpus. Every statement in this item is **SECONDARY — transcribed from the owner's correction, not read by me.**

**Next executable action:** none. **Missing input:** the directory itself, so `retrieval.json` can be read at integration. Do **not** repeat the already-sent source requests; do **not** replay the unchanged origin gate.

---

### Rank 6 — the EMC expression-dataset inventory (W01c / W01d / W01e) · **DESIGN PROSPECT — `NOT RUN` as a paper, and I judge it does not clear the bar**

**Anchors.** W01c: 13 studies, 84 tumour specimens (range 60–84+), 32 obtainable without correspondence (range 32–51); two datasets the repository cites but never treated as data resources (Urbini 2018 n=5 WTS, Filion 2009 n=3, **neither with any data-availability statement**); MI-ONCOSEQ resolved to Davis 2017 PMID 28423517 (6 EMC, obtained only by formal request to journal editors), first GEO cohort to GSE24369. W01d: Urbini 2018 vs Brenca 2019 graded **UNKNOWN at tier D** — same INT-Milano/Treviso pathology files, same two pathologists, so tier B fails on all three conditions and **no independence claim survives**; the 5-frozen=5-WTS coincidence is refuted by partner composition. W01e: obtainable band revised to **44–63** after the Brenca correction.

**Why it does not clear the bar.** The headline number moved 32–51 → 44–63 on one owner correction, and its provenance chain runs through a directory nobody in this campaign can read. `CLOSED-WORK.md` forbids inventing independent cohorts, and W01d has already shown the two largest units are non-independent. What is left is a data-availability census whose central quantity is unstable and whose reference records are unreadable from here. **Do not manufacture a paper from it.**

**Missing input:** the retained `nr4a3-patient-junction-source-2026-09-07/retrieval.json` and a stable obtainable-count denominator, both of which must be read before any number from this line is quoted.

---

### Not ranked, and why

- **W02c / W02d** (endothelial-score variance excess, SD 0.200 vs 0.053–0.095, survives four pre-declared artifact tests): real and well-executed, but the substrate is a 479-gene panel cache, not matrices, and the claim is a variance property of a six-tumour arm. It is a strong internal finding, not a paper.
- **W16 / W16b** (Fréchet bound: ≥59% of metastatic patients with no documented local recurrence, Masunaga n=134): reproduced exactly, exit 0, zero discrepancies. Genuinely distribution-free and never previously computed here. I rank it below Rank 3 because it is registry-derived, sits adjacent to the closed clinical checkpoints, and its admitted set was explicitly refused at two cohorts — it needs the owner's clinical-lane judgement, not a synthesis worker's.
- **W18** (Copas-type publication-selection estimator): complete runnable code, but all four executed runs are **synthetic**, and its own key finding is that selection strength is unestimable. Honest, and not a paper.
- **W17b / W17c / W17d / W17e**: verification of already-published PUB-ATR/PUB-SURFACE-TARGETS quantities. Valuable, but frozen-paper adjacent and out of my scope.

---

## The W11b disposition

### 1. Are complete named final file bodies available, and exactly where are they retained?

**YES — both, complete, and I verified them by extraction rather than by reading the claim.**

They are retained in **W11b's collected report body** at
`/home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/reports/W11b-source-index-consolidated-repair.md` (1,854 lines) at the pinned tip `d3e9c4d8…`:

| Final file | Fence in W11b | Body line range (exclusive of fences) | Extracted lines | My sha256 | W11b's stated sha256 |
|---|---|---|---|---|---|
| `scripts/source_reuse_index.py` | ```` ```python ```` at `:207` → ```` ``` ```` at `:1264` | **208–1263** | 1056 | `b3288598378fd55d26d46ed2e4b6575c2357a57abf71b8fcec7bf28edb8337e3` | `b3288598…` (`:205`) — **match** |
| `scripts/tests/test_source_reuse_index.py` | ```` ```python ```` at `:1270` → ```` ``` ```` at `:1748` | **1271–1747** | 477 | `49208917bba102cd1bceb4ac932046dcab20609f046303f5dc8476954904136a` | `49208917…` (`:1268`) — **match** |

Both bodies are structurally complete and syntactically valid:

```
$ python3 -m py_compile source_reuse_index.py   ; echo $?   -> 0
$ python3 -m py_compile test_source_reuse_index.py ; echo $? -> 0
```

Static AST count on the extracted test body — **18 test methods in one class** `SourceReuseIndexTest`, imports `contextlib, io, json, os, shutil, sys, tempfile, unittest` + `source_reuse_index` (stdlib-only, no plugin dependency). This **independently corroborates the owner's "18 tests"** figure by static structure. It is **not** a test run and I make no claim that it is.

**I did not execute the test suite.** The owner's reserved mechanical executor owns that step; I am not duplicating it and I assert no execution I did not observe.

### 2. The exact test invocation and the appropriate existing test tier

**Invocation** (W11b's own, from the repository root, both runners agreeing):

```
/root/.local/bin/pytest scripts/tests/test_source_reuse_index.py -q
```
and, as the independent cross-runner check that rules out a venv artefact:
```
python3 scripts/tests/test_source_reuse_index.py        # stdlib unittest -> "Ran 18 tests ... OK", exit 0
```

**Tier: `commit-loop`**, by directory membership, not by choice — `scripts/tier-budgets.json:8-9` defines `"commit-loop": {"directories": ["scripts/tests", "research/autonomy/tests", "systems/tests"], "max_test_functions": 1500}`. A file placed flat in `scripts/tests/` is in that tier automatically. Note `scripts/tier_budget.py:78-92`: `count_dir` uses `os.listdir` on the named directory only (non-recursive) and AST-counts functions in files matching `test_*.py` — so a subdirectory would evade the budget, which is why the file must go flat. Also note the tier is **opt-in** (`PREFLIGHT_TESTS=1`, `tier-budgets.json:12`).

**Do not touch the ceiling.** `scripts/tier-budgets.json:5` `_how_to_raise_a_ceiling` already answers the question: *"⛔ NOT BY EDITING THE NUMBER… A cycle that raises a ceiling to land its own test is the shape amendment_guard exists to refuse."*

### 3. Standalone repair verification — **DEMONSTRATED, and it is complete**

These are W11b's recorded runs, with command, exit code and verbatim output, which is what makes them admissible:

- **Final suite:** `/root/.local/bin/pytest scripts/tests/test_source_reuse_index.py -v` → `collected 18 items`, `18 passed in 0.03s`, `EXIT=0` (pytest 9.1.1, Python 3.11.15, `date -u` `Tue Sep 8 02:12:12 UTC 2026`).
- **Negative control:** same test file against the **unrepaired** bundle helper → `7 failed, 11 passed`, `EXIT=1`, with all seven failing test names quoted. Seven of the eight new tests demonstrably pin a repair; W11b states plainly that test 12 passes on the old helper and says why.
- **Runner matrix:** four invocations with exit codes; the one failure (`unittest discover -s scripts/tests -t .` → `ImportError`) is shown to be **a property the existing 21-file `scripts/tests/` tier already has**, not a property of the new file.
- **Nine findings adjudicated by executed probe** — 8 reproduced-and-fixed, F4 reproduced as a mechanism with the review's own cited example **refuted**; zero accepted on reading; neither malformed diff was ported.
- **Safety audit:** exactly one `open()` (line 634, mode `"r"`); no `urllib.request`/`socket`/`requests`/`subprocess` outside a docstring; `main()` returns literal `0` on every path.

**Verdict: the standalone repair is verified.** W11b is one of the few reports in this campaign that carries command + exit code + verbatim output throughout, and it is admissible as an actual test result on its own scratch tree.

### 4. Eligibility for writer integration — **a different question, and the answer is NOT ESTABLISHED**

I am keeping these apart deliberately; the packet must not conflate them.

**What is measured, and where:**

```
$ cd /home/user/Rare-cancers && python3 scripts/tier_budget.py
   ok    commit-loop             1466/1500  test function(s) in 102 file(s)
   ok    modalities              7247/7500  test function(s) in 436 file(s)
   ok    paper-guards             966/1000  test function(s) in 111 file(s)
TIER_EXIT=0
$ ls scripts/source_reuse_index.py scripts/tests/test_source_reuse_index.py
ls: cannot access 'scripts/source_reuse_index.py': No such file or directory
ls: cannot access 'scripts/tests/test_source_reuse_index.py': No such file or directory
```

My own measurement at the pinned tip `d3e9c4d8…` reproduces W11c's **1466** exactly, and confirms the files are **not placed**.

**The base difference is expected and is NOT a `count_dir` malfunction.** W11c's `1466 + 18 = 1484` was measured on the cloud remote `92`-base line of descent (W11c itself recorded reading `b9a0257e…`, not `92abbcb…` and not `4878b9b9…`), and I reproduce 1466 at `d3e9c4d8…`. The owner's previously measured **writer** tier was **1497**. A 31-function gap between two different source bases is exactly what a directory-membership AST counter should produce when the two trees hold different `test_*.py` files — and `commit-loop` aggregates **three** directories (`scripts/tests`, `research/autonomy/tests`, `systems/tests`), so the gap need not even be in `scripts/tests`. I record this as a **source-base difference, not a defect**, and I do not report it as one.

**The consequence, stated in the owner's own arithmetic:** if the writer baseline remains **1497**, then **1497 + 18 = 1515 > 1500**. The pair does **not** fit, and none of the three available ways to make it fit is permitted — the ceiling stays at 1500, no test may be hidden from the accounting, and no 30-case gate may be introduced. All three are recorded closed and I propose none of them.

**Principled integration disposition — `HOLD: VERIFIED-STANDALONE, NOT INTEGRATION-ELIGIBLE ON THE INPUTS AVAILABLE TO ME.`**

I am not authorised to certify integration and I do not have the input that would decide it. Stated exactly:

> **The narrow missing dependency, named:** the **freshly measured `python3 scripts/tier_budget.py` commit-loop count taken on the exact current writer inputs** (the `4878b9b9d1c082cea46e636dad47be419f1fe021` line of descent, or whatever revision the owner is re-measuring), with the tier's per-directory breakdown. Nothing else is missing. The cloud projection **1466 + 18 = 1484 is not writer evidence** and must not be used as one; W11b itself flagged 1484 as arithmetic rather than a post-placement measurement, and W11c confirmed the placement never happened.

Then the disposition resolves mechanically, with no judgement call left:

- If the re-measured writer baseline is **≤ 1482**: placing the pair fits under the unchanged 1500 ceiling. The remaining gate is a real post-placement `python3 scripts/tier_budget.py --check` plus the normal `scripts/preflight.sh` on a settled tree — both currently `PROPOSED (NOT RUN)`.
- If it remains **1497** (or anything **≥ 1483**): the pair does **not** fit, and the correct answer is to leave it unplaced. `tier-budgets.json:5` names the two sanctioned alternatives — ask whether the tests belong in a cheaper tier, and whether something already in the tier has stopped earning its place. Neither is mine to decide, and neither is a licence to move the number.
- Either way: **await the reserved mechanical executor's result** for the extract/hash/run of these exact files. I have not observed it and I assert nothing about it.

**Regardless of the integration disposition, the artifacts and their standalone evidence stay available.** Both complete bodies are retained verbatim in the collected `W11b-source-index-consolidated-repair.md` at the pinned tip, with hashes now independently confirmed by a second party. **A repair that cannot be integrated today is still a repair**, and nothing in this disposition diminishes W11b's executed evidence.

---

## Validation evidence

**RUN.** Environment: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, Python 3.11.15 (`/usr/local/bin/python3`), Claude Code 2.1.42. All execution under `/tmp/claude-0/w23/`; repository read-only.

| # | Command | Exit | Key verbatim output |
|---|---|---|---|
| V1 | `date -u` (start) | 0 | `Tue Sep  8 02:37:06 UTC 2026` |
| V2 | `git rev-parse HEAD` / `git fetch origin claude/confident-bardeen-ji76cd` / `git rev-parse FETCH_HEAD` | 0 | both → `d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4` |
| V3 | `stat -c '%s %n' corpus-snapshot.zip` | 0 | `45840377 corpus-snapshot.zip` |
| V4 | `sha256sum corpus-snapshot.zip` | 0 | `b474cd2f8a0e3fa3a253f5b3135379cb26c15222a94698fc411fd781f6346808` |
| V5 | `python3 -c "import zipfile; …"` | 0 | `members: 6002` · `testzip: None` · `unsafe: 0` · `symlinks: 0` |
| V6 | `git cat-file blob 2a069996…` + `sha256sum` | 0 | `1137077` bytes, `32a802baa78c49bad8a0b6555d282230b618f9c97ebd046a98f9be23dd5aaa2f`, `members: 48`, `testzip: None` |
| V7 | `sed -n '208,1263p' … > source_reuse_index.py; sha256sum` | 0 | `b3288598378fd55d26d46ed2e4b6575c2357a57abf71b8fcec7bf28edb8337e3`, 1056 lines |
| V8 | `sed -n '1271,1747p' … > test_source_reuse_index.py; sha256sum` | 0 | `49208917bba102cd1bceb4ac932046dcab20609f046303f5dc8476954904136a`, 477 lines |
| V9 | `python3 -m py_compile` on both | 0 / 0 | `compile_helper_exit=0`, `compile_test_exit=0` |
| V10 | `python3 -c` AST test-method count on the extracted test body | 0 | `SourceReuseIndexTest 18` · `TOTAL test methods: 18` |
| V11 | `python3 scripts/tier_budget.py` at `d3e9c4d8…` | 0 | `ok commit-loop 1466/1500 test function(s) in 102 file(s)` |
| V12 | `ls scripts/source_reuse_index.py scripts/tests/test_source_reuse_index.py` | 2 | `No such file or directory` (both) — files not placed |
| V13 | `git status --porcelain \| wc -l` | 0 | `0` — tree untouched by me |
| V14 | per-report execution-marker census over all 70 reports | 0 | table below |
| V15 | `date -u` (end) | 0 | `Tue Sep  8 02:40:00 UTC 2026` |

**⚠ Which reports carry actual test evidence and which do not.** A worker report is not a test result. From V14, **ten of the 70 reports carry zero exit-code markers** and therefore contain **no admissible executed evidence** — their findings are retrieval, reading or reasoning, not test results:

`W01b`, `W01d`, `W02`, `W02b`, `W04`, `W07`, `W07b`, `W10`, `W10b`, `W10d`, `W12`.

(Several of these are correctly-scoped retrieval negatives — W01b's 14-route negative and W04's n(EMC)=0 census are honest results, they simply are not test runs.) The reports **richest** in recorded command/exit evidence are `W11` (13), `W12b` (11), `W15d` (11), `W17b` (10), `W13c` (9), `W14b` (9), `W15b` (9), `W11b` (8), `W15` (8), `W17d` (8), `W17e` (8). **Every one of the 70 carries at least one `PROPOSED (NOT RUN)` label**, which is the correct behaviour under the brief.

**PROPOSED (NOT RUN)** — everything below is unexecuted and I claim nothing about it:
- Running W11b's 18 tests. **Reserved to the owner's mechanical executor; deliberately not duplicated.**
- `python3 scripts/tier_budget.py` on the writer `4878` inputs — the named missing dependency.
- `python3 scripts/tier_budget.py --check` with the pair actually placed.
- `scripts/preflight.sh` in any form, and `PREFLIGHT_FULL=1`.
- Placing or running W14's three-generator patch, or repairing `emc_fourth_cohort_quant.py`, in the real tree.
- W19d's DBD-family re-run of the GSE243553 machinery.
- The 6,001-file per-file sha256 corpus pass (coordinator's evidence, not re-run by me).
- Any fetch of GSE243553 `MOESM3_ESM.zip`. **Not attempted, not probed, not routed around.**

---

## Limitations

- **This is advice, not a decision.** I hold no integration, merge, publication or outreach authority. Every disposition here is for the scientific owner to accept, modify or reject.
- **I did not run W11b's tests.** The 18/18 pass result is W11b's recorded evidence, not mine. My contribution is that the two bodies are complete, hash-matched to their stated values, syntactically valid, and structurally contain 18 test methods.
- **I re-verified the whole-ZIP hash and member count, not the 6,001 per-file hashes.** The per-file pass remains the coordinator's evidence.
- **Rank 5 is entirely SECONDARY.** `research/autonomy/nr4a3-patient-junction-source-2026-09-07/` is absent from the pinned tip and absent from the frozen corpus. I transcribed the owner's correction; I did not read `retrieval.json`.
- **The frozen corpus is a selected-file snapshot, not a `93b` checkout.** Absence from it is UNKNOWN, never proof of absence and never source novelty.
- **Rank 3's substrate is chr1 prefixes of third-party marker calls**, 36 shared intervals in total, with ARM 2 resting on n = 4 pairs of which three are EWSR1↔FUS swaps. It is an **ASSOCIATION**. It establishes no mechanism.
- **No clinical claim of any kind appears in this packet.** Computational predictions cannot establish EMC efficacy, safety, selectivity or clinical readiness. There is no wet lab.
- **Ranking is a judgement, not a measurement.** The evidence classes are measured; the ordering is my argued opinion and the owner may reorder it.
- I read the 70 reports through extracted result lines and targeted section reads, not end-to-end. A finding buried outside a report's `Result`/`result:` framing could have been missed.
- Single platform, single point in time: Linux, Python 3.11.15, tip `d3e9c4d8…` as of 2026-09-08T02:40Z. The tier figure 1466 will move as the campaign lands further reports.

---

## Stop condition

Set: branch tip pinned with my own readback; corpus re-verified with my own command output; a small ranked set with named files, hashes and exact source anchors under a strict three-class separation; and the W11b disposition with its standalone-vs-integration split and its named missing dependency. **MET.**

- Tip pinned: `d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4`, with `git fetch` + `git rev-parse` output quoted (later than both `b9a0257e…` and `47aac85f…`).
- Corpus re-verified independently: 45,840,377 B, sha256 `b474cd2f…`, 6,002 members, `testzip()` → `None`, 0 unsafe, 0 symlinks. evidence-4878 capsule also re-verified (1,137,077 B, `32a802ba…`, 48 members).
- Ranked set: six items, each classed DEMONSTRATED / DESIGN PROSPECT (`NOT RUN`) / DUPLICATE REDISCOVERY, each with named files, hashes and file:line or JSON-path anchors, each ending in a next executable action or a named missing input.
- W11b: both bodies located (file + line ranges + independently computed hashes matching), exact invocation and tier given, standalone verification and integration eligibility kept separate, and the single missing dependency named narrowly.
- No paper manufactured. Rank 6 is refused explicitly, and the honest limits of Rank 3 are stated rather than smoothed.

## Tool-call and wall-clock count actually used

**16 tool calls; 2 minutes 54 seconds wall clock** (`02:37:06Z` → `02:40:00Z`). Well inside the ~40/~40 target.

## Next concrete action

**One task, for the owner, ordered by what unblocks the most with the least authority.** Run `python3 scripts/tier_budget.py` on the exact current writer inputs and record the commit-loop total with its per-directory breakdown. That single measurement resolves the W11b disposition mechanically in either direction, and it is the only input this packet lacks. In parallel and needing nothing at all: repair `emc_fourth_cohort_quant.py` (Rank 2) — it is the repository's one advertised-but-unfailable guard and it is wired into a workflow today.

No clinical claim is made anywhere in this packet. Computational predictions cannot establish EMC efficacy, safety, selectivity or clinical readiness.
