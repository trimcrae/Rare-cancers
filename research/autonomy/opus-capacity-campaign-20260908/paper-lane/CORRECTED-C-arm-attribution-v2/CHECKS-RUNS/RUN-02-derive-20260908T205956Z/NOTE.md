# RUN-02 — PRESERVED FAILURE (exit 1), not overwritten

`checks_failed=1`. The failing check was `no_narrative_token_corroboration_predicate_remains`,
detail `suspect_lines=1`.

Diagnosis (recorded before any edit): the single suspect line was the check's OWN regex string
literal inside `main()` —

    r"^(?!\s*#).*leaf_narrative.*(?:in |==|!=|search|match|find|startswith|casefold).*$"

The scan reads the producer's own source, so the pattern matched itself. No expression in the
producer tests the leaf narrative; the false positive is in the guard, not in the logic under test.

Repair applied for RUN-03: the pattern is assembled from two fragments (`"leaf_" + "narrative"`)
so the check's source line no longer contains the literal token and cannot self-match. The guard
was NOT weakened — it still scans the whole executable body for any comparison, membership or
regex operation applied to the narrative field, and still requires the v1 `CORROBORATION` tuple
to be absent. RUN-02 and its exit code 1 stay on the record as the run that actually happened.
