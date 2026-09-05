---
id: DOC-RESEARCHER-PERFORMANCE-2026-09-05
title: Measured preflight and test execution improvements
kind: memo
status: live
date: 2026-09-05
last_verified: 2026-09-05
purpose: Preserve comparable performance evidence and the scope of execution changes.
audience: [maintainers, autonomous research agents]
scope: Local performance measurements; not scientific findings or full release verification.
---

# Measured changes

The historical frozen ASO full release took 2,961 seconds, including 2,239.13 seconds
for manuscripts and 538.22 seconds for modalities. Its receipt and upload bytes are
unchanged. The measurements below are local Windows workloads, not a replacement
for that hosted release evidence or a forecast of the next full CI duration.

| Workload | Before | After | Evidence |
|---|---:|---:|---|
| Five retrospective collector contract tests | 126.94 s | 9.20 s | Both runs: 5 passed; collector logs |
| Four cold-cache manuscript ablations, including baseline checks | 340.809 s | 296.206 s | Four complete result dictionaries identical; 36 versus 27 subprocesses |
| Focused behavior and gate checks | — | 58.35 s | 109 passed, 3 warnings; `focused-tests.log` |

The collector fixture mocked result storage but leaked a real unauthenticated Vast
fleet lookup into board rendering. Each of four mapping tests waited approximately
31 seconds. The fixture now supplies a synthetic empty fleet and synthetic reap and
supervision responses. Every original driver-to-collector scientific assertion still
runs. This measured local reduction is 92.75%.

The ablation harness previously completed each entire witness test batch after a
mutation had already caused a failure, then ran the remaining witness tools. It now
tries standalone tools first, stops when a baseline-green witness detects the
mutation, and uses pytest's first-failure exit only for that mutation probe. A blind
mutation still runs all eligible witnesses. Clean-artifact baselines, subtraction of
already-failing witnesses, all enclosing scientific tests, and manuscript byte
protection remain. The four central samples returned identical status, reason,
witness, quantity-kind and baseline dictionaries. Their subprocess count fell 25%.
Elapsed time fell 13.09%, but concurrent local test work affected timing: the patched
first baseline took 102.60 seconds versus 40.40 seconds. This is not a clean estimate
of hosted CI speedup. One table witness was already red in both baselines and was
explicitly subtracted in both results; it is not counted as having passed.

The ASO first census span also includes an author's ORCID twice, before its
NR4A3 gene identifier. An initial probe spent more than six minutes perturbing identifier digits
without completing that sentence. `metadata-sites.json` demonstrates that eight of
twelve mutation sites were inside those two ORCID representations. The replacement
excludes explicitly labeled or linked ORCIDs only when their MOD 11-2 checksum is
valid; all four other mutation sites remain. Adjacent numerical and word quantities,
unlabeled numbers, and malformed identifiers are covered by behavioral tests. This
does not change the census floor or manuscript text. Only affected ORCID-containing
rows lose their prior ablation cache keys, so an identifier-based old verdict cannot
be reused as quantity evidence. The patched first-span ablation completed in 69.23 seconds, with a green baseline
and an NR4A3 gene-identifier mutation detected; `metadata-after.json` retains the complete
result and all four subprocesses. The earlier run is censored, not a completed
before measurement. The checksum rule follows the official
[ORCID specification](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier).

`scripts/preflight.sh` now preserves its slowest 25 tests for every executed suite in
the durable preflight output. The suite population, flags controlling scope, failure
parsing and final verdicts are unchanged. Shell syntax and the existing suite gating,
dependency, selector and no-silent-skip checks passed. The coordinator runs the normal
preflight once after integration; no full suite was run for this performance branch.

# Reproduction and limitations

`measurements.json` is the result index. `benchmark_ablation.py` loads either the
specified revision's **ablation harness source** or its working-tree replacement,
using the same manuscript and witness data. It forces a cold verdict cache, disables
cache writes, clones before mutation, and records subprocess commands, seconds,
complete outcomes and manuscript hashes. It does not claim to benchmark a historical
release checkout. `--per-paper 1` selects the central covered quantitative sentence
in each of four floored documents. `--offset 0 --paper <document>` selects the first
span of one document. The original before source is
`6dcb5b0140c58b1e9a2f16c093378a355adfeeb2`.

```text
python benchmark_ablation.py --per-paper 1 --revision 6dcb5b0140c58b1e9a2f16c093378a355adfeeb2 --output ablation-before.json
python benchmark_ablation.py --per-paper 1 --output ablation-after.json
python -m pytest research/modalities/tests/test_nrv04_retro_collect_contract.py -q --durations=10
```

The executable and package versions are retained in the ablation JSON. This host used
the bundled Python with `C:/Projects/EMC-Research/.cache/python-deps` on `PYTHONPATH`
and Git's native tools on `PATH`. `PYTEST_DEBUG_TEMPROOT` was set to
`C:/Projects/EMC-Research/.cache/researcher-performance-temp` because the system's
existing pytest temporary root denied access. Initial failed probes are preserved
and explained in `initial-probes.json`; they are excluded from the comparison. The
ablation verdict cache was never populated or rewritten. The ORCID timing before
the change is censored, so no precise speedup is inferred from that interrupted run.
