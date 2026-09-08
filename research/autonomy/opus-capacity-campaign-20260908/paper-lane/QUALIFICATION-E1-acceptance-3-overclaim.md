# Qualification to E1's acceptance term 3 — "no overclaim in either direction: MET"

Recorded 2026-09-08 ~08:56 UTC by the parent, under the existing bounded manuscript continuation and
under separate ownership of the repurposing path from F1. **This is not publication acceptance, and
the canonical-draft identity question raised in `COLLECTION-E1-adjudication.md` remains unresolved.**

## The qualification

`COLLECTION-E1-adjudication.md` grades acceptance term 3 **MET** on the strength of E1's explicit
"neither trial settles this candidate in either direction". That grade was **too broad**, and is
qualified here rather than rewritten.

E1's own new wording overclaimed **against the same section's own admission**. §4.1 states plainly
"Whether any EMC patient was enrolled is unread", yet the same passage and its dependants asserted:

| E1 wording | why it overclaims |
|---|---|
| "**No EMC clinical evidence exists**, but the proteasome-inhibitor class has been tested clinically in sarcoma" (§3.1 Table 2) | asserts **global absence** of clinical evidence from two inspected abstracts |
| "Two published trials give proteasome inhibition to sarcoma patients **outside EMC**" (§4.1) | asserts **demonstrated exclusion** of EMC participants, which is precisely what the section calls unread |
| "It is not an efficacy result, and **neither trial is EMC data**" (§4.1) | same demonstrated-exclusion assertion |
| "Every literature screen behind this menu was scoped to EMC pairings, so a trial naming neither EMC nor *NR4A3* **could not be returned by any of them**" (Appendix A) | asserts **universal search history and retrieval impossibility** from two records |
| "a class-scoped search of the parent histology has been run here for the proteasome axis **alone**" + "The same gap **may hold for any other axis**" (§5) | same universal, extended speculatively to every other axis |

The distinction being restored: **no EMC-specific result in the inspected abstracts and the retained
corpus** is not the same claim as **demonstrated exclusion of EMC participants**, and neither is the
same as **global absence of clinical evidence**. Two abstracts cannot establish the second or third.

## What was changed — eight bounded language replacements, wording only

Applied to `research/manuscripts/repurposing/repurposing-hypotheses.md`. The five statements named by
the orchestrator, plus **three further instances of the identical "outside EMC" exclusion assertion**
(§3.2 closing, §4 tranche 3, §6) that E1 had introduced in the same edit. Those three were narrowed
because leaving them would have left the exact overclaim standing in three other places and put the
paper in contradiction with its own corrected §4.1; the change there is word-level ("in sarcoma
outside EMC" → "in sarcoma"), altering no other meaning.

Representative replacements:

- §3.1 Table 2 → "The inspected abstracts report no EMC-specific clinical result, and the
  proteasome-inhibitor class has been tested clinically in sarcoma [21,22]".
- §4.1 opening → "Two published trials give proteasome inhibition to sarcoma patients, and neither
  abstract inspected here reports an EMC-specific result."
- §4.1 closing → "Neither abstract reports an EMC-specific clinical result, and whether either trial
  enrolled an EMC patient remains unread: that is an absence in what was inspected, not a
  demonstrated exclusion of EMC participants."
- §5 → the universal is replaced by what is on the record: the two class-level reports "were not in
  the preceding draft", were returned by a parent-histology query, and are disclosed in §4.1, with
  an explicit refusal of the two universals — "We do not claim that no screen run here could have
  returned them, nor that the other axes of Table 3 carry the same gap".
- Appendix A → "The preceding draft omitted these two class-level reports."

**The useful disclosure is kept in full.** Both trials, both references, the abstract-level labelling,
the "neither confirms nor refutes" reading, the unchanged in-silico negatives and the Appendix A
supersession row all survive. **No source task, no search, no census, no search-history audit, and no
new input** was run: this is a wording change over material already committed.

## Verification

- **Baseline taken read-only.** `git show HEAD:…repurposing-hypotheses.md` `cmp`-identical to the
  pre-narrowing copy — **no stash, no checkout, nothing touched in the shared tree** while F1's own
  uncommitted work was present.
- Pre-narrowing bytes `ee80467e533d32aa5fd309bc0ea5b16d57f0de1818ed55fa9864a8b07c06e921` (= `d5d3ea2d`
  content, preserved; that history and both logged deviations stand unaltered).
- **Hedges intact after the change**, grepped: 9 `in-silico` mentions, "Neither trial settles this
  candidate in either direction" ×1, "abstract level only" ×2, "Whether any EMC patient was enrolled
  is unread" ×1.
- Word count 5,724 → **5,769 w** of an 8,000 cap; `submission_metrics` exit 0, `0 limit(s) exceeded`.
- `lint_style`, `lint_claims`, `lint_submission_residue`, `lint_asymmetry`, `submission_metrics` all
  **exit 0**. `lint_consistency` **exit 1**, and the single ERROR is
  `mtap-prmt5/emc-mtap-prmt5-hypothesis.md:669` — **F1's concurrent uncommitted file, not this
  edit**; the output names `repurposing` **0** times. Reported, not fixed here, and no gate touched.
- Retained originals: `/tmp/claude-0/e1n-retained/` — `BEFORE.md`, `AFTER.md`,
  `GIT-HEAD-BASELINE.md`, `narrowing.diff`, and each linter's `.out`/`.err` with an echoed exit code.

## Standing

E1's acceptance term 3 is regraded **MET WITH QUALIFICATION**: the direction-of-effect balance E1
struck was sound, but its scope wording asserted exclusion and universality the evidence does not
carry. Terms 1, 2, 4 and 5 are unaffected.
