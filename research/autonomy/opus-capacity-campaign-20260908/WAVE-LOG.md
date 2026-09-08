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
