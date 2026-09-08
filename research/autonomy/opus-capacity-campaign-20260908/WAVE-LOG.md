# Wave log — OPUS-CAPACITY-CAMPAIGN-20260908

Measured facts only. Concurrency figures are `ListAgents` readings with their timestamps,
never the number of workers requested. Per-child model evidence is extracted from child
transcripts at `/tmp/claude-0/.../tasks/<agentId>.output` by
`grep -o '"model":"[^"]*"' | sort -u`; every child so far returns exactly `claude-opus-5`.

| UTC | Event | Measured |
|---|---|---|
| 02:07:45Z | `ListAgents` | 19 rows: **18 running**, 1 completed |
| 02:10:49Z | `ListAgents` | 16 rows: **13 running**, 3 completed |
| — | cumulative dispatches | 48 workers dispatched across all waves |
| — | distinct child model values | **1** — `claude-opus-5` |

## Coordinator corrections applied mid-campaign

1. **Write isolation.** Workers were initially given disjoint write paths inside one working
   tree. That does not satisfy `AGENTS.md`, so all workers were switched to **read-only on the
   Git tree, drafting in response**, with this coordinator as the sole collector. Ten in-flight
   workers were corrected by message; each deleted the file it had created and confirmed a clean
   `git status`.
2. **Model evidence.** An `opus` alias in a dispatch is configuration intent, not proof. Runtime
   model is therefore extracted from each child's transcript and recorded as OBSERVED; the
   children's own self-reports are recorded separately as SELF-REPORT, because no environment
   variable in the container names a model.
3. **Single source-index owner.** Resuming W11 with the arrived capsule created a second
   concurrent source-index worker alongside W11b. W11 was stopped (`TaskStop`, confirmed killed);
   W11b is the sole owner. Its pre-capsule report is retained.
4. **Redundant waiters.** W12b was found running several duplicate Bash polling loops against one
   result file. It was instructed to stop the redundant watchers, keep its real computation, and
   use one bounded completion check.

## Scoped scientific check on lanes adjacent to closed routes

Requested check of W01b, W03b and W06b against the supplied closure records. **No unchanged
failed-gate repeat and no NR4A Perspective reroute was found; none was stopped or redirected.**

- **W03b — ALREADY-KNOWN, and correctly so.** It searched the retained corpus before propagating
  its predecessor's finding, found the NR4A3 exon-2 acceptor documented in `aso_coverage_ladder.py`
  and shipped in both PUB-ASO manuscripts, and declined to file a defect. It identified work as
  closed rather than recreating it, and resolved its predecessor's secondary flag as not-a-defect.
- **W06b — distinct.** It swept a parameter over already-committed pooled outputs, opened no
  retrieval route, and touched none of the closed clinical checkpoints. Its robustness result
  actively *de-prioritises* the Meis-Kindblom retrieval its predecessor had proposed.
- **W01b — novelty checked against retained programme evidence, not merely against its
  predecessor.** Coordinator `rg` over the tracked corpus (excluding this campaign directory)
  confirms Brenca 2019 is retained as a citation and evidence item (`EV-BRENCA-2019`,
  `EV-PMC6766969`) but that **no retained record of any prior attempt on its deposit accession
  exists**, and that the tree holds zero `E-MTAB-`, `EGAS` or `phs` accessions at all. The
  programme demonstrably records a controlled-access accession when it has one — the same
  map-edits file records Haller's `EGAS00001002795` as controlled — which strengthens rather
  than weakens W01b's verdict that Brenca's accession is *unrecovered from here*, and explicitly
  not resolved as controlled-access.

## 2026-09-08 ~02:30Z — coordinator findings and owner corrections

### Gate consequence of the coordinator's own commits (self-reported)
W15b predicted that committing the campaign reports would break `research/manuscripts/lint_citations.py`.
**Confirmed by a clean run** (the earlier `LINT_EXIT=0` reading was `tail`'s status through a pipe, not the
lint's):

```
timeout 600 python3 research/manuscripts/lint_citations.py > /tmp/claude-0/lint.txt 2>&1; echo "LINT_EXIT=$?"
LINT_EXIT=1
```

Every `::error::UNANCHORED …` line names a file under
`research/autonomy/opus-capacity-campaign-20260908/reports/`. The failure is **entirely caused by this
campaign's commits** and did not exist before them.

**Coordinator decision, recorded rather than acted on.** The gate's own error text names two remedies:
anchor each identifier in a fetch product, or add a ledger entry recording *who checked it*. I am applying
neither. I cannot truthfully attribute per-identifier provenance for all of the prose identifiers the
reports introduced, and inventing ledger rows would be exactly the fabrication this gate exists to catch;
`--baseline` refuses to re-run, so there is no accidental path. Narrowing the lint's scan scope to exclude
this directory would be changing a guard to hide an error, which `CLAUDE.md` §6 forbids. The honest state is
therefore: **`lint_citations.py` exits 1 on this branch, the cause is known and bounded to the campaign
report directory, and the remedy is the repository owner's to choose.** No guard was modified.

### Owner corrections received mid-campaign (2026-09-08)
1. **Brenca accessions are already recovered** in `research/autonomy/nr4a3-patient-junction-source-2026-09-07/`
   (correction DOI 10.1002/path.5737; `sources/brenca-ena-runs.tsv` 23 paired libraries / 46 FASTQ links;
   `brenca-origin-gate.csv` + `recover.py` = 8 engineered E-N/T-N aliases, 15 unresolved biological origins).
   PRJNA692081 / SRP301712 are **not a new discovery**. Any recovery of those identifiers or routes is
   classified **DUPLICATE**. W01b's output is preserved. No cohort/independence/patient claim may be built
   on it; 15 unresolved libraries are not 15 patients. Unchanged failed Brenca gates must not be replayed.
2. **PUB-EMC-CLASSIFICATION remains user-rejected and closed** (`portfolio-2026-09-05/recommendation.md:70`).
   `icdo-9231-restriction-audit.json:48` retains unquantified residual misassignment and loss of genuine
   bone-primary EMC; Wagner methods unresolved (abstract omission does not establish absent restriction).
   No new EMC calibration analysis; no reopening on unchanged inputs.
3. **No catalogue-acceptor contract violation was established** by the owner's bounded lookup; none is to be
   inferred from the lane name.
4. W11b remains sole owner of source-index changes. W12b's redundant shell waiters were stopped; its real
   bounded test computation continues. Shell jobs are not research agents.

## 2026-09-08 ~02:40Z — dated correction to this log's own W01b entry

**Corrected, not deleted.** The entry above dated the earlier wave (see the `W01b — novelty checked
against retained programme evidence` bullet) states that *"no retained record of any prior attempt
on its deposit accession exists"*. **That statement is wrong, and it was wrong when written.** It
predates the scientific owner's 02:21Z correction and is contradicted by records the owner has now
named. The original text is retained above so the history reads honestly; this section supersedes it.

**What the retained `93b` records actually hold**, per the owner (I have not read them — see the
verification gap below):

- `research/autonomy/nr4a3-patient-junction-source-2026-09-07/README.md` and `retrieval.json` —
  the canonical record, retaining the correction **DOI 10.1002/path.5737** that identifies the
  accessions, a successful EuropePMC article-XML retrieval, ENA project and run metadata,
  supplementary methods/tables, and the DElite supplement retrieval, each with original URLs and
  hashes.
- `sources/brenca-ena-runs.tsv` — **23 paired libraries / 46 FASTQ links** already enumerated.
- `brenca-origin-gate.csv` and `recover.py` — **8 engineered E-N/T-N aliases** established and
  **15 biological origins unresolved**.
- `research/autonomy/next-paper-2026-09-07/additional-source-provenance/brenca-correction-pubmed.json`
  — links correction **PMID 34216030 / PMC8451045** to **PMID 31020999**.

**Consequences, binding on every lane:**

1. **PRJNA692081 / SRP301712 are already recovered.** Any recovery of those identifiers or routes
   is classified **DUPLICATE**, never a discovery, and never novelty.
2. **W01b's output is preserved.** Its 14-route negative remains an accurate record of what was
   reachable *from this cloud checkout at the time*; what was wrong was this log's inference that
   nothing was retained anywhere.
3. **No cohort, independence or patient claim may be built on it.** There is no accession-to-case
   key and no independent patient or specimen key. **15 unresolved libraries are not 15 patients**,
   and libraries are not specimens.
4. **Do not repeat the already-sent source requests and do not replay the unchanged origin gate.**
5. W01e has already acted on this: it corrected its inventory row for Brenca to
   `DEPOSITED — accession known and public`, classified the correction **DUPLICATE**, held the
   specimen count at the paper-stated **12** rather than 23 or 15, and moved the obtainable band
   from 32–51 to **44–63**.

⚠ **Verification gap, stated rather than smoothed over.** `research/autonomy/nr4a3-patient-junction-source-2026-09-07/`
**does not exist in this cloud checkout** at any HEAD this campaign has read, and it is not present
in the verified 5,996-file frozen corpus snapshot either. Every statement in this section is
therefore **SECONDARY — transcribed from the owner's correction, not read**. W01e independently
confirmed the directory's absence and graded its own corrected row the same way. The coordinator
should re-verify this section against `retrieval.json` when the branches are integrated.

## 2026-09-08 ~02:45Z — writer-4878 tier baseline received; W11b integration disposition updated

**Evidence update only.** No worker was dispatched for this, no gate was changed, and no integration
occurred. This supersedes the projection arithmetic carried in the W23 synthesis packet's dispatch;
it does not supersede any worker's own measurement of its own base.

**Measured by the scientific owner on the actual writer 4878** — `scripts/tier_budget.py --check`,
**exit 0**:

| Tier | Measured | Ceiling | Files |
|---|---|---|---|
| commit-loop | **1497** | 1500 | 105 |
| modalities | 7249 | 7500 | — |
| paper-guards | 973 | 1000 | — |

**Consequence for the unchanged 18-test W11b addition: 1497 + 18 = 1515 against an unchanged
ceiling of 1500 — it exceeds by 15.** The earlier figure of 1484 was `1466 + 18` on the **cloud
remote 92 base**, which is a different source tree, not a `count_dir` malfunction: three independent
cloud workers (W11c at `b9a0257`, W11d and W17f at `7d08121`) each measured commit-loop at
**1466/1500 across 102 files** on this checkout. The writer carries 3 more files and 31 more test
functions than the cloud checkout. That difference is expected and is now confirmed from both sides.

**Integration disposition, updated and stated as two separable things:**

1. **Standalone repair verification is not blocked by this.** The owner has recovered the exact
   inline W11b helper and test bodies and both declared hashes match; the reserved private executor
   is running the deterministic standalone final/negative-control suites and one bounded real Brenca
   identifier lookup. **Those results are pending. No pass may be claimed from started execution**,
   and this coordinator is not duplicating that executor.
2. **Eligibility for writer integration is, on the measured baseline, NEGATIVE as a whole.** 18 tests
   do not fit in 3 functions of headroom. The three ways to make them fit are all refused here:
   raising the ceiling to land the code is what `tier-budgets.json::_how_to_raise_a_ceiling` exists
   to prevent; hiding tests from accounting is the shadowing failure `tier_budget.py::_shadowed`
   detects; and a 30-case gate is an invented acceptance criterion. **None is taken.**

**What the campaign measured that bears on the disposition, all on the cloud base and all read-only:**

- **W11d** exhausted both sanctioned alternatives by measurement. *No cheaper tier exists*:
  `scripts/tests` (commit-loop) is already the cheapest correct home; `modalities` has more headroom
  (253) but is the most expensive tier to run and wrong by subject; `paper-guards` has identical
  headroom and runs in the paper gate commit-loop is exempt from. *Nothing has stopped earning its
  place*: **0 of 102 files and 0 of 1466 functions are unreached, 0 shadowed, 0 unparseable, 0
  module-level skips** — W11d found and overturned its own nine-file false positive rather than
  publishing it. It also recorded a latent hole: `count_dir` uses `os.listdir`, not `os.walk`, so a
  test in a *subdirectory* of a tier directory would be budgeted by nothing while still running on
  every push. **Measured unexploited (all five tier directories have zero subdirectories), and
  explicitly not to be used as a routing manoeuvre.**
- **W11d's recommendation, which survives the new baseline in shape but not in size:** land the
  smallest useful subset rather than all of it, and re-run `tier_budget.py` after placement instead
  of projecting. On the writer's 3 functions of headroom, even that subset is smaller than the
  18-test pair.
- **W17f** independently reproduced commit-loop **1466/1500** on this checkout and separately asks
  for **8** functions of `modalities` headroom (7247 → 7255), which is a different tier and does not
  compete with W11b's request.

**Therefore: the honest disposition is that the W11b artifact and its standalone evidence are kept
and remain available regardless of integration, and integration of the full 18-test addition is not
eligible against the unchanged 1500 ceiling on the measured 1497 writer baseline.** A declared
ceiling amendment with this measurement attached is the only remaining path, and it is the
scientific owner's decision, not a worker's or this coordinator's. The owner retains integration
authority; nothing here integrates, merges, or publishes anything.

## 2026-09-08 ~02:47Z — owner's terminal execution of the W11b pair; and the bounded PMID smoke query

**Evidence update only. No worker was dispatched for this, no test was re-run here, no gate was added
or changed, no repair was made, and no route was reopened.** These are the **scientific owner's actual
terminal measurements**, recorded as such. They are **not** this coordinator's execution and **not**
the earlier worker's unverified claim; the two are kept distinct below.

### 1 · Standalone execution of the hash-matched W11b helper/test pair — OWNER-MEASURED

| Run | Result | Exit | Wall |
|---|---|---|---|
| Final helper + final tests | **18 passed** | **0** | 0.734 s |
| **Negative control** — same tests against the **unchanged original** helper | **7 failed, 11 passed** | **1** | 0.688 s |

The negative control is retained as evidence in its own right: the suite discriminates repaired from
unrepaired, so the 18/18 is not a vacuous pass. **Initial harness attempts ended in pytest-cache
cleanup and are retained, not deleted.** Only the runtime `cache_dir` was relocated under a verified
private TEMP; **no supplied code, test or guard was changed** to obtain the pass. Exact executor
packet paths and hashes will follow when supplied — **this log must not invent them**, and this
coordinator did not perform, observe or duplicate that execution.

This **supersedes** the standalone-verification line of the W23 packet (which correctly recorded
W11b's own claim as the worker's, and explicitly declined to assert an execution it had not
observed). W23's independent contribution stands: it extracted both bodies from the collected report,
recomputed both sha256 values and matched W11b's declared hashes exactly
(`b3288598…` helper, `49208917…` test), compiled both, and counted 18 test methods statically.

### 2 · The one authorized real-source smoke query — bounded parser-coverage evidence

Query for **PMID 31020999** over the retained README / `retrieval.json` / correction JSON returned
**`unresolved_not_indexed`, zero matches, exit 0**. A literal `rg` by the owner found `31020999`
present at `resultList.result[0].commentCorrectionList.commentCorrection[0].id` with `source='MED'`;
the **explicitly named** `pmid` in that record is **34216030**, and the README names Brenca by
**DOI 10.1002/path.5284**.

**What this is:** an exact **semantic coverage limit** of the index — the identifier is retained, but
it is reachable only as a comment-correction back-reference, not under the field the query reads.
**What this is not:** it is **not** evidence the source is absent, **not** a newly required repair,
and **not** grounds for a new gate or acceptance criterion. No repeat query, no new test and no
retrieval was performed. The Brenca closure is unchanged: those accessions and routes remain
**DUPLICATE**, and nothing here reopens them.

### 3 · Disposition — the three things stay separate

1. **Demonstrated standalone improvement** — established by the owner's terminal run above, with a
   real negative control. Recorded as measured.
2. **Exact semantic coverage limit** — recorded as a bounded observation about how one identifier is
   reachable in the retained records. It creates no obligation.
3. **Integration eligibility** — unchanged and **negative**. The confirmed writer baseline is
   **1497/1500**; the unchanged 18-test addition projects **1515**, which exceeds the ceiling. It
   cannot be integrated unchanged. **The ceiling is not raised, no test is hidden from the
   accounting, and no invented gate is introduced.** Integration authority remains the scientific
   owner's.

**No scientific or paper novelty is inferred from standalone code success.** A lookup helper passing
its own suite says nothing about EMC, and nothing here bears on efficacy, safety, selectivity or
clinical readiness.

## 2026-09-08 ~02:52Z — W11b execution packet fetched and inspected (transcription replaced by evidence)

**This section replaces the transcribed execution provenance of the ~02:47Z section with bytes this
coordinator actually fetched, hash-checked and read.** The packet was **not re-run**; every result
below is read out of its retained records. Nothing in it was executed.

**Transport, verified by this coordinator:**

```
git fetch origin codex/opus-cloud-inputs-20260908   →  ad34f06b..ba8b66ea
git rev-parse …                 = ba8b66ea786eec2c7db6ac5ba391fa5f8fd413b5   (matches owner)
git log --format='%H %P' -1     parent ad34f06b53c2fb41f0b3d7949239b8d2951ac61e   (matches owner)
git cat-file blob ba8b66ea:research/autonomy/cloud-inputs-2026-09-08/w11b-execution-evidence.zip
  size          97,191 bytes                                        (matches owner's 97191)
  sha256        70da0993c8fe95e8764c31b5634ab7f430abe9e764e8809633a8f88887b8de8d   (MATCHES)
  members       54                                                  (matches owner's 54)
  zipfile.testzip()  → None                                         (all members CRC-clean)
  unsafe paths  0        symlinks 0        uncompressed 309,338 bytes
```

Extracted **once**, read-only, to `/tmp/claude-0/w11b-exec/extracted/` — a separate context area
**beside** the frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/`. Neither overlays the working
tree; no second copy was made. The six corpus parts are unchanged and were not re-fetched.

**Owner-declared anchors, checked against the extracted bytes:**

| Anchor | Declared | Measured here | |
|---|---|---|---|
| `final-summary.json` sha256 | `a4ffa5c0…9d21a3` | `a4ffa5c01a8cd4ef3419a77b120228083addd3435e1046dff249d488279d21a3` | **MATCH** |
| `file-manifest.json` sha256 | `eff50342…5475e0` | `eff50342b2bbb02cbffa309b2df8c694cbfe6056c1256bb48b8b21e9625475e0` | **MATCH** |
| packet excluding manifest | 53 files / 300,460 bytes | 53 files / 300,460 bytes | **MATCH** |

The transport `phase4-verification.json` (sha256 `38c1a73a…e19d3c12`) is the **owner's** record and was
**not supplied in this container**; it is recorded as an anchor and **not inspected**. No local path is
invented for it.

**What the packet's own records say** (read from `final-summary.json`, not re-run):

- `cloud_commit` `47aac85f874a57a6f981c3432abcf16980968aec`; `report_sha256` `18f17d87…`,
  `helper_sha256` `b3288598…`, `test_sha256` `49208917…` — the last two are **the same hashes W23
  independently recomputed** from the collected W11b report body, so the executed files are the
  delivered files.
- **Initial attempts:** both terminated **exit 1 during pytest final cache-staging cleanup rejected by
  a private TEMP guard** — *"not terminal passing test runs"*. Original stdout/stderr/argv retained in
  `execution-result.json`. These failures are preserved, not discarded.
- **Corrected positive:** `18 passed in 0.14s`, process **exit 0**, wall **0.734 s**.
- **Corrected negative control** (the same tests against the **unchanged original** helper):
  `7 failed 11 passed in 0.25s`, process **exit 1**, wall **0.688 s**, with all seven failing test
  names recorded, and `negative_matches_reported_control_counts: true`.
- `all_source_and_guard_hashes_unchanged: true`; the only change was `runtime_only_change` — the
  pytest `cache_dir` placed inside a fresh run-specific TEMP; **no code, test or guard edit**.
  `cleanup_events: 17`, all allowed; `network_events: 0`.
- **The one authorized smoke query:** `PMID31020999` → **exit 0**, `0.141 s`, normalised `31020999`,
  scheme `pmid`, 3 files, no scope warnings, **`state: unresolved_not_indexed`, `matches_count: 0`**,
  inputs unchanged. This is the parser-coverage limit already recorded at ~02:47Z; it is **not**
  evidence the source is absent and creates no repair obligation.

**Files retained in the packet** include `report.original.md`, both `positive/` and `negative/` trees
carrying the exact helper and test bodies, four `*.audit.jsonl` runtime audits, four
`*.execution.json` receipts, both harness freezes, `run_exact.py` / `run_exact_2.py`,
`runtime-safety/sitecustomize.py`, and the smoke receipt and stdout.

**Nothing in the disposition changes.** Standalone repair verification is now **evidenced rather than
transcribed**; the semantic coverage limit stands as a bounded observation; and **integration
eligibility remains negative** — the confirmed writer baseline is **1497/1500** and the unchanged
18-test addition projects **1515**. Wording elsewhere that a declared amendment is the only remaining
path is **not** authority to raise the ceiling, and this coordinator does not raise it. The scientific
owner retains any later integration disposition. The W23 packet remains **advisory**, and its pre-02:40
body remains **historical** beside this later evidence.

## 2026-09-08 ~02:58Z — CORRECTION: the junction-source directory IS in the frozen corpus

**Corrected, not deleted.** Two earlier entries in this log, and W23's packet, state that
`research/autonomy/nr4a3-patient-junction-source-2026-09-07/` is absent from the verified frozen
corpus. **That is FALSE.** The error was a path-root mistake by this coordinator: the
repository-relative root of the supplied files is
**`/tmp/claude-0/frozen-corpus/extracted/corpus/`**, not `/tmp/claude-0/frozen-corpus/extracted/`.
Searching the outer directory finds nothing and looks like absence. The earlier text is retained
above; this section supersedes it, and it supersedes it on evidence rather than on assertion.

**Inspected here, in the extracted corpus, this coordinator's own `stat`/`sha256sum`:**

| Corpus path (root `…/extracted/corpus/`) | bytes | sha256 |
|---|---|---|
| `research/autonomy/nr4a3-patient-junction-source-2026-09-07/README.md` | **7,227** | `55dc009f52373fa28faf9aa22037db552f9625aee7646f3d3d8957794e1750c2` |
| `research/autonomy/nr4a3-patient-junction-source-2026-09-07/retrieval.json` | **3,870** | `a5216ca7edcf00694cf58625f85cf991f77d3b85aea1a19902aef998aefee273` |
| `research/autonomy/next-paper-2026-09-07/additional-source-provenance/brenca-correction-pubmed.json` | **2,599** | `c83fbdbf5adb54721a59088f5db824d099960bc56d05b191019e74ea9a343172` |

All three byte counts match the owner's, and all three are members of the **same** whole-ZIP already
verified at sha256 `b474cd2f8a0e3fa3a253f5b3135379cb26c15222a94698fc411fd781f6346808`. The directory
holds **13 files** in total: the two above plus `brenca-origin-gate.csv`, `compare_published_calls.py`,
`coordinator-verification.json`, `delite-model-metadata.csv`, `published-call-comparison.json`,
`recover.py`, and `sources/{brenca-article.xml, brenca-ena-runs.tsv, brenca-project.xml,
delite-article.xml, urbini-article.xml}`. **This is inspection of already-supplied context — no
re-upload, no new source request and no retrieval was performed.**

The README's own front matter reads `id: DOC-NR4A3-PATIENT-JUNCTION-SOURCE-20260907`,
`status: live`, `date: 2026-09-07`, and its opening paragraph states verbatim:

> "The proposed original patient-read study did not pass its access and specimen-identity gate.
> No raw reads were downloaded or aligned."

**What is corrected, and what is not.**

1. **Corrected:** every statement in this log and in W23 of the form *"absent from the frozen
   corpus"* for this directory. The correct statement is: **absent from this cloud checkout at every
   HEAD the campaign has read, present in the frozen corpus, and now read there.**
2. **Corrected:** the SECONDARY grading of the ~02:40Z Brenca section is upgraded **only for the two
   files actually opened here**; everything transcribed from the owner that this coordinator has
   still not read stays SECONDARY.
3. **NOT corrected, and unchanged:** W01b, W01e and W23 stated honestly that they had **not read**
   these files, and that honesty is preserved rather than rewritten. Their reports stand.
4. **NOT changed by this at all:** the Brenca closure. The accessions remain **already recovered and
   DUPLICATE, never novelty**; the directory's own README records that its access-and-identity gate
   was **not passed**; 23 ENA libraries are **not** 23 patients and the paper-stated specimen count
   is 12. No cohort, independence or patient claim follows from this correction.
5. **Operational consequence:** the same root-path correction must be applied before relying on any
   repository-novelty claim made against the corpus — W23 rank 3's novelty search in particular was
   run against the older remote checkout and the outer directory, so its scope must be restated
   before it is used.

W21b independently reached the same finding from the other direction, enumerating the 13 files as
corpus-only and flagging that the incorrect standing fact was propagating through dispatch prompts.
It also drafted two further corrections — to W01e's *"only EGA accession anywhere in the tree"*
sentence (four more are live-tree, two more corpus-only; its substantive verdict survives) and to
W13c's *"identified here for the first time"* for Giner 2022/2023 (the full citation is already in
the live tree at two paths). Both are retained in `reports/W21b-*` for the owner.

## 2026-09-08 ~03:05Z — W25 candidate-merit check returns NOVELTY FAILS

The scientific owner's commissioned one-slot check on the GSE243553 partner-binding prospect
(W23's rank 3) is complete. **It recommends declining admission, on novelty — not on statistics.**
It is **advice for the owner, not a decision**; nothing here admits, rejects, integrates or publishes
anything, and the owner may weigh it differently.

**1 · Novelty fails, on two retained repository documents.**
`research/autonomy/next-paper-2026-09-07/selection.md` L56–58, verbatim:

> "Frenkel and colleagues already report **fusion-family clustering and context-invariant chromatin
> effects** in PROD-ATAC (doi:10.1038/s41587-024-02347-4). Those ideas, generic gene-set scoring and
> mapping peaks to genes are not claimed as new methods."

and `research/autonomy/nr4a3-program-source-2026-09-07/README.md` L53:

> "The primary PROD-ATAC paper already reports **context-invariant chromatin effects, family
> clustering**, native-control comparisons and NR4A3 fusion gain-of-function chromatin behavior.
> **None is proposed as novelty here.**"

The same selection memo carries a stop rule that fires exactly here: *"Stop this proposed experiment
if … primary prior art already reports the proposed contribution."* After subtraction, what remains
of the four reports is **two data-hygiene corrections** (the 128 `peakset_inventory` entries are 32
real BEDs plus 64 AppleDouble forks and 32 non-interval tables; `median_width` is a constant 500 bp)
and a qualitative re-detection of a published result on a truncated substrate. **That is not a paper.**

**2 · The "403 blocks the genome-wide data" premise is FALSE at the repository level — and this
changes nothing about the denial itself.** The base-`93b` tracked-file map records, with sizes:
`nr4a3-program-source-2026-09-07/sources/markers.zip` **788,065 B**,
`outputs/peaks.tsv` **3,041,469 B**, `sources/paper.html` **301,282 B** (the PMC13105821 full text),
plus `peak-gene-links.tsv`, `program-membership.tsv`, `tss.tsv` — 60 tracked paths in all. The
in-corpus `outputs/bed-members.tsv` gives per-member path, byte size, sha256 and peak counts for all
**32** genome-wide BEDs, and `source-manifest.jsonl` records the successful Springer retrieval at
788,065 bytes. **The ZIP five reports recorded as unrecoverable was fetched, hashed and committed on
2026-09-07.** ⛔ **This is a snapshot-selection and branch-lineage gap, not an access gap, and it is
NOT authority to probe the 403.** The CONNECT denial from this container is real, was not tested by
W25, and remains a denied route. W23 rank 3's "exact missing input" line and W19e's closing "progress
requires the genome-wide peak sets, and that route is a recorded 403" are both wrong as stated.

**3 · The statistics held.** W25 attacked the result twice and could not break it: the whole-name
permutation **is** a valid exact randomization test despite severe pair dependence, because each draw
recomputes the dependent statistic on the same fixed pair topology; and a density-quartile-stratified
null **strengthened** the 3′ effect (p at the Monte-Carlo floor) while leaving the 5′ negative
negative. It found one real, previously unnamed defect — **uncontrolled window depth**, where W19e's
primary class sits at median min-depth **17.0** against a panel median of **5.5**, and J rises ~8.7×
with depth across the panel — and measured that controlling it moves the residual only 0.1608 →
0.1459 with p unchanged. **The statistics are not why this fails.** The dependence is nonetheless
severe: 15 "observations" from **8** peaksets, one entering 5 of them.

**4 · Corrections owed, routed not applied.** (a) The claim that **clinical practice assumes
fusion-partner interchangeability** (W20b's Question, repeated by W23) is **UNSOURCED** — a corpus
search found no source stating it, and every `interchangeab` hit asserts the opposite about other
things. It must be dropped or anchored. (b) W19e is a **reproducible exploratory successor on
recycled data**, not a prespecified confirmation or held-out validation: its confirming set contains
W19d's discovering 7 pairs, on the same 32 peaksets. Its own discipline was good and should be
credited; the framing must be corrected. W19g independently carried the same correction.

**5 · The one thing that could change the disposition**, and it is a verification step, not an
analysis: deliver `sources/paper.html` into a readable checkout and read whether the publication
already reports 3′-determined, 5′-invariant peak location at family resolution. If yes, the line
closes. If no — and only then — the identical machinery runs on the genome-wide BEDs, where the
0.4%-of-genome window, the 4–28-interval depths and the whole depth confound vanish at once, and the
pair-dependence problem remains and would need a cluster-aware statistic rather than a larger p.
