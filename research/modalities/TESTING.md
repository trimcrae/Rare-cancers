---
id: DOC-TESTING
title: Testing & methodology rigor — research/modalities
level: L4
kind: memo
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `memo` from its location under research/modalities/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# Testing & methodology rigor — research/modalities

This note exists because of a **near-miss**: an interim pocket-enumeration script produced a spurious
"orthosteric pocket = 0.026 (undruggable)" result and a tentative "off-by-one" diagnosis — both wrong,
caught and retracted in-session before they reached any manuscript number. The authoritative value is
the original (now regenerated and confirmed): orthosteric **Pocket 5 = druggability 0.495, residues
406-534**. The root cause of the false alarm was that `nr4a3_structure.py` mapped fpocket residue files
to pockets by *assuming* the file index equalled the info.txt pocket number (`pocket{N}_atm.pdb` ⇄
"Pocket N"). That convention *does* hold in this environment, so the original output was correct — but
the assumption is a latent risk, and the interim script's combination of a wrong alpha-sphere count
with a tentative index shift manufactured a plausible-looking wrong answer. It was possible because
(a) the code assumed an external tool's convention instead of deriving it, and (b) there were no tests.
These rules prevent a repeat.

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
7. **★★ ASSERT THE PROPERTY, NEVER A LABEL OR A POPULATION COUNT (two of these were fixed on
   2026-07-31, both having failed on changes that HONOURED what they existed to protect).** A test
   that pins the *wording* of a readout, or the *size* of a growing set, has both failure modes
   backwards: it goes red on every legitimate addition, and it stays green through the illegitimate
   one.
   - `tests/test_on_demand_tier.py` asserted `count(gate self-dispatches forwarding on_demand) == 2`.
     Adding a third gate that **correctly** forwarded the flag turned the suite red on `main`; a
     fourth gate that *dropped* it would have left the count at whatever was last typed. It now
     derives both sides — `LAUNCH_TASKS` from `ternary_vast_launch.MODES`, and the dispatch scan
     parses backslash-continued **blocks** (a line-based scan finds nothing, because the task and the
     tier sit on different continuation lines).
   - Two tests asserted `"approved rate" in cell` — the **label** on an in-flight `$/ns` cell. Both
     now assert the **absolute rate is present**, which is the actual invariant
     (`tests/test_buy_line_invariant.py`, `tests/test_inflight_usd_per_ns.py`, which carry the note
     in place).
   **The check that catches this while writing the test: run a NEGATIVE CONTROL.** Break the property
   deliberately and confirm the test fails *with a message naming the property*, then restore and
   byte-compare. Both fixes above were verified that way, and so was the
   `vast_min_cuda_floor_12_6` entry in `pinned-figures.json`.

## Running the tests

```bash
pip install pytest
python -m pytest research/modalities/tests -q
```

### ⚠ Two ways of running these that waste real time

- **THE FULL SUITE IS NOT FREE: 4097 passed, 29 skipped, ~6 min 55 s** (measured 2026-07-31 in the dev
  sandbox, `python3 -m pytest tests -q -p no:cacheprovider`). **Do not have every subagent run all of
  it.** Run the **targeted modules** you touched while iterating, and **one full run before merging** —
  that is what the green figure above is for. **And they contend:** with two agents' suites live at once
  in this sandbox, `ps` showed them at **54.6 % and 96.4 % CPU** — concurrent full runs take each other's
  throughput, so N agents do not cost N × 7 min, they cost more.
- **`until ! pgrep -f "pytest tests/"` NEVER EXITS — IT MATCHES ITSELF.** `pgrep` excludes only its own
  PID, **not its ancestors**, and the shell running the wait loop has the literal pattern in its own
  `argv`. Reproduced 2026-07-31: with no pytest running at all, the loop spun until `timeout` killed
  it (rc 124), and `pgrep -af` showed the two matches were the loop's own `bash -c` processes.
  **The same trap kills, not just waits:** `pkill -f "pytest tests -q…"` issued to clear a stale run
  **also killed the replacement launched in the same command** (both exited 144, measured minutes later
  the same day) — the new process matched the pattern the moment it started. If you must pattern-kill,
  kill by **PID**, or make the replacement's argv deliberately different.
  Wait on a **completion marker in the log** instead — the pattern this repo already uses:
  ```bash
  <cmd> > /tmp/run.log 2>&1; echo "EXIT=$?" >> /tmp/run.log     # then poll for EXIT=
  ```
  or, if you must match a process name, break the literal with the bracket trick: `pgrep -f "[p]ytest
  tests/"`.

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
