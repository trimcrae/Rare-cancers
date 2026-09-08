# W25 executed scientific computation — preserved verbatim

Collected by the campaign parent collector at 2026-09-08T03:15:10Z from the live container
scratch directory /tmp/claude-0/w25/, which W25 declared as the sole location of its execution.
Copy only: the files were not re-run, not modified, and not reconstructed from memory.
W25's report recommended AGAINST paper admission. A negative admission does not remove the
obligation to retain executed scientific computation, so the bodies are retained here.
Report: reports/W25-gse243553-candidate-merit.md (committed at 98a0833f).

## Files as found in /tmp/claude-0/w25/

| file | bytes | mtime (container) | sha256 |
|---|---|---|---|
| `audit.py` | 6104 | 2026-09-08 02:59:39 | `cebb61842081d495545b707758100a960d924de10b5f17082abe036fd64b069c` |
| `strat.py` | 2650 | 2026-09-08 03:01:39 | `c5d1df302dbfad897582a6945528b2344c073e7da386c2561052039343a2a259` |

Sizes match the two W25 declared in its report (6104 B and 2650 B). No other file was present
in that directory; nothing is recorded here as missing.

## Bounded command and exit evidence, quoted from the W25 report

Successful invocations:

- RUN 10: `cd /tmp/claude-0/w25 && python3 --version && time python3 audit.py; echo "EXIT=$?"` -> `real 1m4.809s`, **EXIT=0**
- RUN 11: `time python3 strat.py; echo "EXIT=$?"` -> `real 0m35.059s`, **EXIT=0**

The two failed development invocations, retained rather than discarded (W25 report, RUN 10 and RUN 11):

- `audit.py`, first invocation: **exited 1** on an `AttributeError` — `peakset_inventory` is a dict, not a list. The fix touched only that loop.
- `strat.py`, intermediate invocation: **exited 1** on a `KeyError: 'res2'` from an `exec`-truncated prelude. The fix restricted the loop to the one defined statistic.

Both scripts are stdlib-only and deterministic given seed=20260908. audit.py rebuilds the
substrate from the two committed JSONs and computes the windowed Jaccard, density quintiles and
residual, class census, per-class dependence counts, window-depth tables, the density x depth
cell residual, and the whole-name permutation under both residual definitions. strat.py reuses
that prelude via exec and runs the density-quartile-stratified permutation.

## Scope of this collection

Read and copy only. Nothing was re-run, no code was changed, no worker was launched, and no
test or acceptance gate was created. The exit codes above are W25's actual measurements as
recorded in its report, transcribed here, not re-measured by the collector.
