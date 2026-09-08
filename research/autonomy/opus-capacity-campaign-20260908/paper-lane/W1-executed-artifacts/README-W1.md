# W1 — PROPOSED Supplementary Table S3 (lane record)

Worker W1, EMC capacity campaign, 2026-09-08. **PROPOSED only. Nothing applied. No shared path
written. No git write.**

## Intended scope, and where it was established

- `research/manuscripts/dependency/emc-atr-collaborator-package-changelog.md` (2026-08-10 entry,
  "Additions rather than corrections"): "**Supplementary Table S3**, holding the cut coordinates,
  assembled cDNA length and open reading frame for each reported junction, from
  `emc-fet-construct-designs.json`". Same file, line 39: "**Supplementary Table S3** carrying the
  per-junction assembly coordinates". S3 serves the §4.1 six-step construct-assembly procedure.
- `paper-lane/R1-executed-artifacts/DECISION-MEMO.md` U3: the missing input is "Supplementary Table
  S3's per-junction cut coordinates, assembled cDNA length and ORF"; R1 declined on scope, noting the
  source artifact exists but "the table was not built in this lane".
- `paper-lane/U1-executed-artifacts/U1-DECISION-MEMO-on-R1-proposal.md` U3: "SPLIT — PARTLY
  RESOLVABLE … Table S3 is a data-assembly task against a committed input … Buildable by whoever the
  coordinator tasks, without network."

Scope taken: one row-set covering **each reported junction** — the four emitted constructs — with
cut coordinates, assembled cDNA length and ORF, plus the two reported fusions for which the input
records **no** sourced transcript-level junction.

## Files

- `PROPOSED-supplementary-table-s3.md` — the table.
- `build_table_s3.py` — assembly script. Reads the one committed JSON, copies leaves, emits the
  table + provenance. Computes no value. Run from the repo root:
  `python3 /tmp/claude-0/w1-lane/build_table_s3.py`
- `PROVENANCE-table-s3.md` / `provenance-cells.json` — JSON path for all 96 cells.
- `faithfulness_check.py`, `FAITHFULNESS-CHECK-RESULT.txt` — the check and its output.
- `NEGATIVE-CONTROL-RESULT.txt` — the same checker failing on a single deliberately altered cell,
  showing it can detect a discrepancy rather than always passing.
- `START-END-STATE.txt` — date/HEAD/status at start and end.

## UNRESOLVED

- **CUT — genomic breakpoint coordinates**: the input carries transcript/cDNA-level coordinates only.
  No genomic breakpoint key exists for any emitted construct. Marked UNRESOLVED for all four rows,
  not derived from exon ranks.
- **FUS::NR4A3, TCF12::NR4A3**: every assembly field UNRESOLVED — the input records no
  transcript-level junction (TCF12 genomic-only, intron 5). Their recorded status strings are copied
  verbatim rather than replaced by an inferred junction.

## Integrity

`registered_predictions` (4 entries, at
`rgg_dose_calibration_and_predictions.registered_predictions`) was read only and is byte-identical
to HEAD; the check asserts this. No efficacy, safety, selectivity or clinical claim is made here —
the input's own status line and all five `_limits` entries are carried into the table verbatim. No
content-policy refusal occurred.
