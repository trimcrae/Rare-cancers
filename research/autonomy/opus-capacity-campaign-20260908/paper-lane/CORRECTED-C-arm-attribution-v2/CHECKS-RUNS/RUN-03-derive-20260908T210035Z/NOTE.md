# RUN-03 — PRESERVED FAILURE (exit 1), not overwritten

`checks_failed=1`, same check `no_narrative_token_corroboration_predicate_remains`, now with
`suspect_lines=0`. The remaining failure came from the check's OTHER self-referential literal:
`"CORROBORATION" not in body` is itself a line of `body` containing that word (source line 619).
The producer's real code has no such tuple — the only other occurrence, line 13, is inside the
module docstring, which is excluded from `body`.

Repair for RUN-04: the compared token is assembled as `"CORROB" + "ORATION"`, so the check's own
source no longer contains it. The guard is unchanged in strength.

RUN-03's map/checks outputs and its exit code 1 stay on the record as the run that happened.
