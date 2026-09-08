<!-- COLLECTION DEFECT, recorded rather than papered over.
     Agent id ad1aea9c42ff2bd3e. Its transcript file
     /tmp/claude-0/.../tasks/ad1aea9c42ff2bd3e.output is a REAL FILE OF ZERO BYTES —
     not a symlink into the subagent store like every other worker's, and not something
     this collector truncated. The report body reached the coordinator only through the
     delivered task result. What follows is a COORDINATOR TRANSCRIPTION of that result,
     not a mechanical extraction: it records the measurements and their evidence class
     and does not reconstruct the worker's prose or re-derive its numbers. Treat every
     figure below as SECONDARY (transcribed), not as the worker's PRIMARY record.
     The model set could not be asserted from the transcript for the same reason. -->

# W24c — the D3 control against R07 (transcribed record)

**Status: PARTIAL. The primary report is lost to a zero-byte transcript.** The worker ran and
returned; the coordinator received its result and records what it measured.

## What the worker measured

- **W24's capability discriminator is wrong.** R07 and R08 are indistinguishable on the
  probe-count drift class D3. Both exit 1, both print the identical drift list
  `['probe_counts_sha256']`, and both leave the corruption on disk rather than laundering it.
- Three arms, each restored from pristine baselines so the arms are independent:
  **A (unpatched)** exit 0, corruption survives undetected — the defect reproduced, matching
  W14d exactly. **B (R07-patched)** exit 1, `DRIFT: ['probe_counts_sha256']`.
  **C (R08-patched)** exit 1, same drift list. All three arms reproduced the three committed
  hashes when run clean, so no arm's environment was degraded.
- **R07's diff applies cleanly**: `git apply --check` and `git apply` both exit 0, no fuzz, no
  rejection, no hunk offset. So the arm the question turns on carries no transcription caveat.
- **The worker flagged its own weakest arm rather than smoothing it.** W14d's diff is not
  machine-applicable (abbreviated hunk headers) and omits the `--check` branch, so arm C is a
  faithful REBUILD of R08 as documented, not R08 as W14d executed it, with an unexplained
  off-by-one in the diff line count (93 against W14d's stated 92).
- Cause, read from the code: `load_inputs()` rehydrates run counts from the probe TSV itself,
  so `derive()` reproduces a drifted body bit-for-bit and no byte comparison can see a count
  drift. Adding `probe_counts_sha256` to the drift-key tuple is the whole of the D3 fix, and
  BOTH patches add it. What was only in R08 was the executed test, not the capability — and
  as of this run that is no longer true either.
- Consequence for the owner: the choice collapses to size, test count and memory cost, all of
  which W24b already tabulated. The worker ruled on nothing and landed nothing.
- Unchanged by this run: both repairs still move zero committed counts, hashes and bytes; the
  CI row is still non-blocking, so a repaired guard is still not an enforced one; and the
  residual hole neither repair closes — a consistent edit to both the TSV and the JSON still
  passes — is untouched.

## Coordinator disposition

- The live tree was verified byte-unchanged: the target script and all three artifacts carry
  their committed hashes at the worker's start and end.
- Its named next action is routed: correct W24's routing index row so the owner does not read
  a discriminator that does not exist, and note that R07's behaviour on drift classes D1 and D2
  remains unmeasured.
- An environment note the worker raised and this coordinator acted on: container disk reached
  99 percent during its run, with roughly 25 GB held in other workers' scratch copies. The
  coordinator has since released the scratch of every completed worker, taking free space from
  2.9 GB to 22 GB.
