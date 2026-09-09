# Validation evidence — three-pin guard maintenance

Date 2026-09-09 UTC. Branch `claude/confident-bardeen-ji76cd`. Only file changed in the tracked
tree by this batch: `research/manuscripts/pinned-figures.json`
(153842 B / sha256 966efbe20322fc28137cb82fbf2bdad292db06954eba2f8c4ce26a5747fa82d3
→ 158004 B / sha256 1287de4e134424e36d1ff0b2531b47a794af8cc4e1706b2d9ca401b6bb226c23).
No manuscript number, source JSON, producer arithmetic or clinical record was touched.

## Positive check — the existing lint

```
$ python3 research/manuscripts/lint_consistency.py
lint_consistency: 0 ERROR across 29 target file(s)
EXIT=0
```

stderr empty. The three `A-key-missing` errors on
`analyses.B_outcome_by_partner.disease_specific_death` are gone because the pins that referenced
that withdrawn path are retired, not because any predicate was relaxed. No unrelated failure was
reported by this lint.

⚠ Honest sequencing: this lint was run twice. The first run (same command, same output, EXIT=0)
was taken on an intermediate version of the three new entries that used the LINE-BY-LINE form of
rule A. Inspecting `check_artifact_figures` showed that branch discards the capture group
(`quoted = _nums(ln)` — every number on the row), so each pin could have been vouched for by a
neighbouring cell's digits; the linter's own `_check_flattened` docstring names the capturing
form as the strong one. The entries were changed to `"match": "flattened"` with capturing
patterns, and the run above is the one on the settled edit. Both runs are reported rather than
only the last.

## Negative fixtures — disposable, outside the tracked tree

Harness: `<scratchpad>/fp3/negfix.py`, sha256 9e7338f7819267bf186457ee4b4dd9ee4571d36edc5886968bde8bce9e129ac9. It copies only the artifact and the
manuscript into a `tempfile.TemporaryDirectory`, perturbs the copy, and calls the UNMODIFIED
`lint_consistency.check_artifact_figures` with `repo=<tempdir>`. Nothing is written to the
tracked tree; `git status --ignored` shows no fixture residue.

| # | fixture | required | result |
|---|---|---|---|
| C0 | unperturbed baseline, all three pins | pass, 0 findings | OK |
| C1 | artifact `taf15_arm.percent` 42.9 → 41.9 | reject | OK — A-figure-mismatch, quotes [42.9] |
| C2 | artifact `comparator_arm.percent` 6.2 → 7.2 | reject | OK — A-figure-mismatch, quotes [6.2] |
| C3 | artifact `fisher_exact_two_sided_p` 0.0672 → 0.0772 | reject | OK — A-figure-mismatch, quotes [0.0672] |
| C4 | manuscript row cell 42.9 → 41.9 | reject | OK — A-figure-mismatch, quotes [41.9] |
| C5 | manuscript row cell 6.2 → 7.2 | reject | OK — A-figure-mismatch, quotes [7.2] |
| C6 | manuscript row cell 0.0672 → 0.0772 | reject | OK — A-figure-mismatch, quotes [0.0772] |
| C7 | neighbouring local-recurrence row's identical 1/16 = 6.2 % → 9.9 % | comparator pin unaffected | OK — 0 findings |
| C8 | artifact TAF15 leaf set to the comparator's own 6.2 | reject | OK — A-figure-mismatch, quotes [42.9] |
| C9 | artifact comparator leaf set to TAF15's own 42.9 | reject | OK — A-figure-mismatch, quotes [6.2] |

`negfix.py` exit 0 for C0–C7 ("8 fixtures, 0 not as required"); C8–C9 were run as a second
bounded cross-vouching pass, "2 cross fixtures, 0 not as required".

Each rejection message quotes exactly ONE captured number, which is what shows the capture group is
live: the pin is bound to its own table cell, not to "some number on the row". C7 and C8/C9 are the
specificity half — a guard that fires on the wrong row or is vouched for by the neighbouring cell
would be a green build over an unchecked figure.

## Not done, and still outstanding

- No producer run, no new statistic, no source lookup, no figure render, no full test suite, no
  preflight, no review rerun. Nothing was committed, added or pushed.
- The historical five-module FP suite still stands at **107 failed / 75 passed, UNRESOLVED**. Only
  **20** of the 107 failure bodies were ever inspected (they stop at `KeyError:
  disease_specific_death`); the other 87 are unadjudicated. This batch does not triage that suite
  and makes no claim about it.
- The parent's dated correction withdrawing the "lost live headline" diagnosis already exists at
  commit **b58e0ed89** and is reused, not duplicated. The correction register's N14 historical
  origin wording is unchanged.
