<!-- COLLECTION DEFECT, recorded rather than papered over.
     Agent id aff1e01f23e32b105 ; transcript
     /tmp/claude-0/.../tasks/aff1e01f23e32b105.output
     OBSERVED runtime model set in that transcript: ["claude-opus-5"].
     The worker's full report body is NOT recoverable from its transcript: the deepest
     text scan of every JSON node in that file yields a 68-character trailing turn and
     nothing else. The body reached the coordinator only through the delivered task
     result. What follows is therefore a COORDINATOR TRANSCRIPTION of the delivered
     result, not a mechanical extraction, and it is deliberately partial: it records the
     measurements and their evidence class, and does not reconstruct the worker's prose,
     its verbatim command output, or its exit codes from memory. Treat every figure below
     as SECONDARY (transcribed), not as the worker's PRIMARY record. -->

# W06g — mortality-decomposition re-label matrix (transcribed record)

**Status: PARTIAL. The primary report is lost to a transcript defect.** The worker ran and
returned; the coordinator received its result and is recording what it measured. Nothing
here was re-derived by the coordinator and nothing was invented.

## What the worker measured

- It enumerated **75 numeric scalars** published by `research/manuscripts/emc-mortality-decomposition.json`,
  found **57 distinct values**, **15 values shared by more than one path**, giving **21 same-value pairs**.
- It separated definitional identities from coincidences **by execution**, not by inspection:
  one control run reproducing the committed artifact byte-for-byte, a 300-run randomised
  perturbation sweep, two 200-run coupled/decoupled sweeps, and targeted adversarial probes —
  701 generator runs in total, all exit 0.
- **Three re-labels, not one.** W06f's `smallest_coherent_share_pct` finding is joined by
  `antitumour_ceiling_pct_points` (the disease mortality restated in percentage points, an
  identity the repository's own test name already asserts) and by the 10-year
  `observed_competing_mortality_pct_at_10y`, which is the median share multiplied by the
  complement of the lowest all-cause survival rather than a second measurement.
- **A fourth, weaker one:** on the committed inputs `antitumour_ceiling_pct_points_range` is
  exactly the reversed disease-specific-survival range subtracted from 100, at both horizons —
  but this is NOT definitional, since the coherence filter can drop the extreme pairing, and
  it failed in roughly a quarter to a third of perturbed runs.
- **The counterexample that keeps the method honest:** the two `pairings_undefined` fields are
  both 0 and stayed equal in all 201 randomised runs, which reads as definitional and is not.
  A random draw on (0.05, 0.99) can never reach the exact values that create an undefined
  pairing; a targeted probe separated them. A 300-input equality is not proof of a
  definitional identity.
- **One published row does not add up**, by 0.1 point: `direct_cause_split[1]` publishes
  `all_cause_mortality_pct` 34.5 while `disease_mortality_pct + competing_mortality_pct`
  is 31.0 + 3.4 = 34.4. This is independent rounding of each term, not a data error and not
  a registry problem — no count and no interval is wrong.
- **The prose check is a clean NEGATIVE.** No prose anywhere in the tree presents any of these
  identities as an independent confirmation or as a newly measured quantity; every re-label is
  printed next to its own derivation. The tree's independence claims concern two different
  artifacts and the worker found no shared numeric input between them, which it correctly
  called "checked and not contradicted" rather than verified.

## Coordinator disposition

- The worker was read-only; `git status --porcelain` was empty at its start and end, and it ran
  only on a sandboxed copy because the generator writes its output file unconditionally.
- Its named successor question — whether the relative-survival and cause-split artifacts are
  genuinely independent — was dispatched to W06h to be settled by execution rather than reading.
- The collector was hardened after this: it now falls back to concatenating all assistant turns
  and then to a deep scan of every text node. Neither recovers this body, so the defect is
  recorded here rather than hidden by a silently short file.
