# Testing & methodology rigor — research/modalities

This note exists because a **silent off-by-one bug shipped a wrong number into a manuscript**:
`nr4a3_structure.py` mapped fpocket residue files to pockets by *assuming* the file index equalled
the info.txt pocket number (`pocket{N}_atm.pdb` ⇄ "Pocket N"). fpocket's file numbering did not match
that assumption, so a **0.495 druggability was attached to the wrong residues** in
`nr4a3-structure-assessment.json` (and propagated into the degrader design spec). It was possible
because (a) the code assumed an external tool's convention instead of deriving it, and (b) there were
no tests. These rules prevent a repeat.

## Rules

1. **Derive external-tool conventions from data; never assume them.** Indexing, column layouts,
   1-vs-0 based numbering, file ordering — read them out of the data and verify. Example:
   `fpocket_lib.map_files_to_pockets` matches alpha-sphere fingerprints (counts, then coordinates)
   instead of trusting the filename integer.
2. **Fail loud, never silently mis-map.** Ambiguous or inconsistent data must raise, not guess.
   The mapping asserts a bijection; ties without disambiguating data raise `ValueError`.
3. **Parsing/mapping logic lives in pure, dependency-free modules** (`fpocket_lib.py`,
   `residue_map.py`) — no I/O, no openmm/mdtraj/fpocket imports — so it is unit-testable locally
   without a GPU, AWS, or the external binaries. The SageMaker scripts import these libs; the fixed
   code *is* the tested code.
4. **Every parser has a unit test against a fixture with a known answer**, including a regression
   test for the specific bug class (`test_mapping_follows_data_not_filename` encodes file indices
   that disagree with pocket numbers and asserts the mapping follows the data).
5. **CI gates experiments.** `.github/workflows/tests.yml` runs the suite on every push/PR. Keep it
   green before dispatching any SageMaker run.
6. **Real runs log an audit cross-check.** `nr4a3_fpocket_enumerate.py` prints the data-derived
   file→pocket mapping next to the naive +0/+1 assumptions, so the true convention is visible and
   auditable in the job log — and any future divergence is caught by eye, not assumed away.

## Running the tests

```bash
pip install pytest
python -m pytest research/modalities/tests -q
```

## What's covered

- `tests/test_fpocket_lib.py` — info.txt parsing, residue/coord parsing, and the data-derived
  file→pocket mapping (happy path with offset filenames, coordinate tie-break, and the fail-loud
  paths: count mismatch, unmatched count, ties without coordinates).
- `tests/test_residue_map.py` — Pocket/CV residue→position mapping for both the AF2-preserved and
  renumbered-from-1 topologies (the zero-match bug the first SASA run hit).

## Caveat (honest limit)

The fixtures encode our understanding of fpocket's output format. They prove the *logic* is correct
and convention-independent, but the first real run's audit log (rule 6) is what confirms the format
assumptions against actual fpocket output — review it before trusting a fresh pocket result.
