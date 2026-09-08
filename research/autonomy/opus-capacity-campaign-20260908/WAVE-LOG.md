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
